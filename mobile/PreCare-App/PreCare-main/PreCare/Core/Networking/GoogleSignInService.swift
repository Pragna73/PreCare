import AuthenticationServices
import Foundation

/// Runs Google sign-in through Supabase's hosted OAuth endpoint.
///
/// Deliberately uses `ASWebAuthenticationSession` rather than the GoogleSignIn
/// SDK: the session captures its own callback scheme, so this needs no Swift
/// package, no `CFBundleURLTypes` entry, and no Xcode project changes. Supabase
/// performs the token exchange and hands back a normal Supabase session in the
/// redirect fragment.
enum GoogleSignInError: LocalizedError {
    case notConfigured
    case cancelled
    case noTokens(String?)

    var errorDescription: String? {
        switch self {
        case .notConfigured:
            return "Supabase is not configured. Add SupabaseURL to Config.plist."
        case .cancelled:
            return "Sign-in was cancelled."
        case .noTokens(let detail):
            if let detail, !detail.isEmpty {
                return "Google sign-in failed: \(detail)"
            }
            return "Google sign-in did not return a session."
        }
    }
}

struct SupabaseOAuthTokens {
    let accessToken: String
    let refreshToken: String
    let expiresAt: Int
}

@MainActor
final class GoogleSignInService: NSObject {
    static let shared = GoogleSignInService()

    /// Must also be listed under Authentication -> URL Configuration ->
    /// Redirect URLs in the Supabase dashboard, or Supabase refuses the redirect.
    private let callbackScheme = "precare"
    private let redirectURL = "precare://auth-callback"

    private var session: ASWebAuthenticationSession?

    private override init() {
        super.init()
    }

    func signIn() async throws -> SupabaseOAuthTokens {
        guard AppConfig.isSupabaseConfigured,
              var components = URLComponents(string: "\(AppConfig.supabaseURL)/auth/v1/authorize")
        else {
            throw GoogleSignInError.notConfigured
        }

        components.queryItems = [
            URLQueryItem(name: "provider", value: "google"),
            URLQueryItem(name: "redirect_to", value: redirectURL)
        ]

        guard let authURL = components.url else {
            throw GoogleSignInError.notConfigured
        }

        let callbackURL = try await presentWebAuthSession(url: authURL)
        return try parseTokens(from: callbackURL)
    }

    private func presentWebAuthSession(url: URL) async throws -> URL {
        try await withCheckedThrowingContinuation { continuation in
            let session = ASWebAuthenticationSession(
                url: url,
                callbackURLScheme: callbackScheme
            ) { callbackURL, error in
                if let error {
                    let code = (error as? ASWebAuthenticationSessionError)?.code
                    continuation.resume(
                        throwing: code == .canceledLogin
                            ? GoogleSignInError.cancelled
                            : error
                    )
                    return
                }

                guard let callbackURL else {
                    continuation.resume(throwing: GoogleSignInError.noTokens(nil))
                    return
                }

                continuation.resume(returning: callbackURL)
            }

            session.presentationContextProvider = self
            // Google requires a real login each time unless the user has a
            // session; sharing the Safari cookie jar makes that far smoother.
            session.prefersEphemeralWebBrowserSession = false

            self.session = session

            if !session.start() {
                continuation.resume(throwing: GoogleSignInError.noTokens("Could not open the sign-in page."))
            }
        }
    }

    /// Supabase returns tokens in the URL *fragment*, not the query string.
    private func parseTokens(from url: URL) throws -> SupabaseOAuthTokens {
        let fragment = URLComponents(url: url, resolvingAgainstBaseURL: false)?.fragment ?? ""
        var values: [String: String] = [:]

        for pair in fragment.split(separator: "&") {
            let parts = pair.split(separator: "=", maxSplits: 1).map(String.init)
            guard parts.count == 2 else { continue }
            values[parts[0]] = parts[1].removingPercentEncoding ?? parts[1]
        }

        if let errorDescription = values["error_description"] {
            throw GoogleSignInError.noTokens(errorDescription)
        }

        guard
            let accessToken = values["access_token"],
            let refreshToken = values["refresh_token"]
        else {
            throw GoogleSignInError.noTokens(values["error"])
        }

        return SupabaseOAuthTokens(
            accessToken: accessToken,
            refreshToken: refreshToken,
            expiresAt: Int(values["expires_at"] ?? "") ?? 0
        )
    }
}

extension GoogleSignInService: ASWebAuthenticationPresentationContextProviding {
    func presentationAnchor(for session: ASWebAuthenticationSession) -> ASPresentationAnchor {
        UIApplication.shared.connectedScenes
            .compactMap { $0 as? UIWindowScene }
            .flatMap(\.windows)
            .first { $0.isKeyWindow }
            ?? ASPresentationAnchor()
    }
}
