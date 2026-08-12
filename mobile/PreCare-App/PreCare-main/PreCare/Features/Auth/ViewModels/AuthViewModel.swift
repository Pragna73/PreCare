import Foundation
import Combine

@MainActor
final class AuthViewModel: ObservableObject {

    @Published var fullName = ""
    @Published var email = ""
    @Published var password = ""
    @Published var phone = ""
    @Published var emergencyContact = ""

    @Published var isLoading = false
    @Published var errorMessage: String?

    @Published var resetEmail = ""
    @Published var resetSuccessMessage: String?
    @Published var isSendingReset = false

    private let apiClient: APIClient

    init(apiClient: APIClient? = nil) {
        self.apiClient = apiClient ?? APIClient.shared
    }

    func loginUser(onSuccess: @escaping () -> Void) {
        guard !email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
              !password.isEmpty else {
            errorMessage = "Email and password are required."
            return
        }

        isLoading = true
        errorMessage = nil

        Task {
            do {
                let session = try await apiClient.login(
                    LoginPayload(
                        email: email.trimmingCharacters(in: .whitespacesAndNewlines),
                        password: password
                    )
                )

                SessionStore.shared.saveAccessToken(
                    session.accessToken,
                    refreshToken: session.refreshToken,
                    userID: session.userID,
                    role: session.role
                )

                if let user = try? await apiClient.me() {
                    SessionStore.shared.saveUser(
                        name: user.fullName,
                        email: user.email,
                        role: user.role,
                        phone: user.phoneNumber,
                        emergencyContact: user.emergencyContact
                    )
                }

                isLoading = false
                onSuccess()
            } catch {
                isLoading = false
                errorMessage = error.localizedDescription
            }
        }
    }

    func registerUser(onSuccess: @escaping () -> Void) {
        let cleanName = fullName.trimmingCharacters(in: .whitespacesAndNewlines)
        let cleanEmail = email.trimmingCharacters(in: .whitespacesAndNewlines)
        let cleanPhone = phone.trimmingCharacters(in: .whitespacesAndNewlines)
        let cleanEmergency = emergencyContact.trimmingCharacters(in: .whitespacesAndNewlines)

        guard !cleanName.isEmpty else {
            errorMessage = "Full name is required."
            return
        }

        guard !cleanEmail.isEmpty else {
            errorMessage = "Email address is required."
            return
        }

        guard !password.isEmpty else {
            errorMessage = "Password is required."
            return
        }

        guard !cleanPhone.isEmpty else {
            errorMessage = "Mobile number is mandatory."
            return
        }

        guard cleanPhone.count >= 10 else {
            errorMessage = "Please enter a valid 10-digit mobile number."
            return
        }

        guard !cleanEmergency.isEmpty else {
            errorMessage = "Emergency contact phone (family member) is mandatory to alert relatives during high-risk detection."
            return
        }

        guard cleanEmergency.count >= 10 else {
            errorMessage = "Please enter a valid 10-digit emergency contact phone number."
            return
        }

        isLoading = true
        errorMessage = nil

        Task {
            do {
                let userID = try await apiClient.register(
                    RegisterPayload(
                        email: cleanEmail,
                        name: cleanName,
                        password: password,
                        role: "PATIENT",
                        phone: cleanPhone,
                        emergencyContact: cleanEmergency
                    )
                )

                let session = try await apiClient.login(
                    LoginPayload(
                        email: cleanEmail,
                        password: password
                    )
                )

                SessionStore.shared.saveAccessToken(
                    session.accessToken,
                    refreshToken: session.refreshToken,
                    userID: session.userID ?? userID,
                    role: session.role
                )

                SessionStore.shared.saveUser(
                    name: cleanName,
                    email: cleanEmail,
                    role: .patient,
                    phone: cleanPhone,
                    emergencyContact: cleanEmergency
                )

                if let user = try? await apiClient.me() {
                    SessionStore.shared.saveUser(
                        name: user.fullName,
                        email: user.email,
                        role: user.role,
                        phone: user.phoneNumber ?? cleanPhone,
                        emergencyContact: user.emergencyContact ?? cleanEmergency
                    )
                }

                isLoading = false
                onSuccess()
            } catch {
                isLoading = false
                errorMessage = error.localizedDescription
            }
        }
    }

    func signInWithGoogle(onSuccess: @escaping () -> Void) {
        isLoading = true
        errorMessage = nil

        Task {
            do {
                if AppConfig.isSupabaseConfigured {
                    let tokens = try await GoogleSignInService.shared.signIn()
                    let session = try await apiClient.completeGoogleSignIn(tokens)

                    SessionStore.shared.saveAccessToken(
                        session.accessToken,
                        refreshToken: session.refreshToken,
                        userID: session.userID,
                        role: session.role
                    )

                    if let user = try? await apiClient.me() {
                        SessionStore.shared.saveUser(
                            name: user.fullName,
                            email: user.email,
                            role: user.role,
                            phone: user.phoneNumber,
                            emergencyContact: user.emergencyContact
                        )
                    }

                    isLoading = false
                    onSuccess()
                } else {
                    let googleEmail = "google.user@example.com"
                    let googlePassword = "GoogleUser123!"

                    let session: AuthSession
                    do {
                        session = try await apiClient.login(LoginPayload(email: googleEmail, password: googlePassword))
                    } catch {
                        let _ = try await apiClient.register(
                            RegisterPayload(
                                email: googleEmail,
                                name: "Google User",
                                password: googlePassword,
                                role: "PATIENT",
                                phone: "9876543210",
                                emergencyContact: "9885757159"
                            )
                        )
                        session = try await apiClient.login(LoginPayload(email: googleEmail, password: googlePassword))
                    }

                    SessionStore.shared.saveAccessToken(
                        session.accessToken,
                        refreshToken: session.refreshToken,
                        userID: session.userID,
                        role: session.role
                    )
                    SessionStore.shared.saveUser(
                        name: "Google User",
                        email: googleEmail,
                        role: .patient,
                        phone: "9876543210",
                        emergencyContact: "9885757159"
                    )

                    isLoading = false
                    onSuccess()
                }
            } catch {
                isLoading = false
                errorMessage = error.localizedDescription
            }
        }
    }

    func sendPasswordReset(onSuccess: (() -> Void)? = nil) {
        guard !resetEmail.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            errorMessage = "Please enter your email to reset password."
            return
        }

        isSendingReset = true
        errorMessage = nil
        resetSuccessMessage = nil

        Task {
            do {
                try await apiClient.requestPasswordReset(email: resetEmail.trimmingCharacters(in: .whitespacesAndNewlines))
                isSendingReset = false
                resetSuccessMessage = "Password reset instructions sent to your email."
                onSuccess?()
            } catch {
                isSendingReset = false
                errorMessage = error.localizedDescription
            }
        }
    }
}
