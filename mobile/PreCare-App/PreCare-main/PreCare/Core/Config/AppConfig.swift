import Foundation

/// Runtime configuration, loaded from the bundled `Config.plist`.
///
/// Only client-safe values belong here. The Supabase service-role key, the Resend
/// key and the Gemini/NVIDIA keys stay on the FastAPI backend — anything shipped
/// inside the app bundle is readable by anyone who downloads the app.
enum AppConfig {
    private static let values: [String: Any] = {
        guard
            let url = Bundle.main.url(forResource: "Config", withExtension: "plist"),
            let data = try? Data(contentsOf: url),
            let plist = try? PropertyListSerialization.propertyList(from: data, format: nil),
            let dictionary = plist as? [String: Any]
        else {
            print("[Config] Config.plist not found in bundle — falling back to defaults. Copy Config.example.plist to Config.plist.")
            return [:]
        }
        return dictionary
    }()

    private static func string(_ key: String, default fallback: String) -> String {
        // Info.plist wins so a build configuration can override without editing Config.plist.
        if let value = Bundle.main.object(forInfoDictionaryKey: key) as? String, !value.isEmpty {
            return value
        }
        if let value = values[key] as? String, !value.isEmpty {
            return value
        }
        return fallback
    }

    /// Base URL of the PreCare FastAPI backend.
    static let apiBaseURL: URL = {
        let raw = string("APIBaseURL", default: "http://127.0.0.1:8000")
        guard let url = URL(string: raw) else {
            preconditionFailure("[Config] APIBaseURL is not a valid URL: \(raw)")
        }
        return url
    }()

    /// Supabase project URL, e.g. https://<project-ref>.supabase.co
    static let supabaseURL = string("SupabaseURL", default: "")

    /// Publishable anon key. Safe to ship — access is bounded by row-level security.
    static let supabaseAnonKey = string("SupabaseAnonKey", default: "")

    /// Restrict this key to the app's bundle ID in the Google Cloud console.
    static let googleMapsAPIKey = string("GoogleMapsAPIKey", default: "")

    static var isSupabaseConfigured: Bool {
        !supabaseURL.isEmpty && !supabaseAnonKey.isEmpty
    }
}
