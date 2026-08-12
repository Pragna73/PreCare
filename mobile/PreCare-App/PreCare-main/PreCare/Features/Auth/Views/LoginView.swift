import SwiftUI

struct LoginView: View {

    @StateObject private var vm = AuthViewModel()
    @EnvironmentObject var router: AppRouter
    @State private var showForgotPasswordSheet = false

    var body: some View {
        VStack(spacing: 24) {

            Spacer().frame(height: 40)

            VStack(spacing: 4) {
                HStack {
                    Image(systemName: "heart.fill")
                        .foregroundColor(Color(hex: "#FF2D6F"))
                    Text("PreCare")
                        .font(.system(size: 18, weight: .bold))
                }
                Text("AI Healthcare Platform")
                    .font(.system(size: 12))
                    .foregroundColor(.gray)
            }

            Spacer().frame(height: 30)

            Text("Welcome back")
                .font(.system(size: 26, weight: .bold))

            VStack(spacing: 16) {
                InputField(
                    icon: "envelope",
                    placeholder: "Email address",
                    text: $vm.email
                )

                VStack(alignment: .trailing, spacing: 8) {
                    InputField(
                        icon: "lock",
                        placeholder: "Password",
                        text: $vm.password,
                        isSecure: true
                    )

                    Button("Forgot password?") {
                        vm.resetEmail = vm.email
                        vm.resetSuccessMessage = nil
                        vm.errorMessage = nil
                        showForgotPasswordSheet = true
                    }
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(Color(hex: "#FF2D6F"))
                }
            }

            Button {
                vm.loginUser {
                    router.goToDashboard()
                }
            } label: {
                Text(vm.isLoading ? "Signing in..." : "Sign in")
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity, minHeight: 54)
                    .background(Color(hex: "#FF2D6F"))
                    .cornerRadius(14)
            }
            .disabled(vm.isLoading)

            HStack(spacing: 12) {
                Rectangle()
                    .fill(Color.gray.opacity(0.3))
                    .frame(height: 1)
                Text("or")
                    .font(.system(size: 13))
                    .foregroundColor(.gray)
                Rectangle()
                    .fill(Color.gray.opacity(0.3))
                    .frame(height: 1)
            }

            Button {
                vm.signInWithGoogle {
                    router.goToDashboard()
                }
            } label: {
                HStack(spacing: 12) {
                    GoogleLogoView(size: 22)
                    Text("Sign in with Google")
                        .font(.system(size: 16, weight: .semibold))
                }
                .foregroundColor(.primary)
                .frame(maxWidth: .infinity, minHeight: 54)
                .background(
                    RoundedRectangle(cornerRadius: 14)
                        .stroke(Color.gray.opacity(0.35), lineWidth: 1)
                )
            }
            .disabled(vm.isLoading)

            if let errorMessage = vm.errorMessage {
                Text(errorMessage)
                    .font(.footnote)
                    .foregroundColor(.red)
                    .multilineTextAlignment(.center)
            }

            Spacer()

            HStack {
                Text("Don't have an account?")
                    .foregroundColor(.gray)

                NavigationLink("Sign up") {
                    RegisterView()
                }
                .foregroundColor(Color(hex: "#FF2D6F"))
            }

            Spacer().frame(height: 20)
        }
        .padding(.horizontal, 24)
        .navigationBarBackButtonHidden(true)
        .sheet(isPresented: $showForgotPasswordSheet) {
            ForgotPasswordSheetView(vm: vm, isPresented: $showForgotPasswordSheet)
        }
    }
}

struct ForgotPasswordSheetView: View {
    @ObservedObject var vm: AuthViewModel
    @Binding var isPresented: Bool

    var body: some View {
        VStack(spacing: 24) {
            HStack {
                Text("Reset Password")
                    .font(.system(size: 22, weight: .bold))
                Spacer()
                Button {
                    isPresented = false
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .font(.title2)
                        .foregroundColor(.gray.opacity(0.6))
                }
            }

            Text("Enter your email address below and we'll send you instructions to reset your password.")
                .font(.system(size: 14))
                .foregroundColor(.secondary)
                .multilineTextAlignment(.leading)

            InputField(
                icon: "envelope",
                placeholder: "Enter registered email",
                text: $vm.resetEmail
            )

            if let successMsg = vm.resetSuccessMessage {
                Text(successMsg)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.green)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }

            if let errorMsg = vm.errorMessage {
                Text(errorMsg)
                    .font(.footnote)
                    .foregroundColor(.red)
                    .multilineTextAlignment(.center)
            }

            Button {
                vm.sendPasswordReset {
                    // Success handled by resetSuccessMessage
                }
            } label: {
                Text(vm.isSendingReset ? "Sending..." : "Send Reset Link")
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity, minHeight: 52)
                    .background(Color(hex: "#FF2D6F"))
                    .cornerRadius(14)
            }
            .disabled(vm.isSendingReset)

            Spacer()
        }
        .padding(24)
        .presentationDetents([.height(380)])
    }
}

struct GoogleLogoView: View {
    var size: CGFloat = 22

    var body: some View {
        ZStack {
            Text("G")
                .font(.system(size: size * 0.85, weight: .black, design: .default))
                .foregroundStyle(
                    LinearGradient(
                        stops: [
                            .init(color: Color(hex: "#4285F4"), location: 0.0),  // Blue
                            .init(color: Color(hex: "#EA4335"), location: 0.35), // Red
                            .init(color: Color(hex: "#FBBC05"), location: 0.7),  // Yellow
                            .init(color: Color(hex: "#34A853"), location: 1.0)   // Green
                        ],
                        startPoint: .topTrailing,
                        endPoint: .bottomLeading
                    )
                )
        }
        .frame(width: size, height: size)
    }
}


