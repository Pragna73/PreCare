

import SwiftUI

import Combine



@MainActor
final class AppRouter: ObservableObject {

    @Published var path = NavigationPath()
    @Published var isLoggedIn: Bool = UserDefaults.standard.bool(forKey: "isLoggedIn")

    // MARK: - Navigation Helpers
    func push(_ route: AppRoute) {
        path.append(route)
    }

    func pop() {
        if !path.isEmpty {
            path.removeLast()
        }
    }

    func goToDashboard() {
        UserDefaults.standard.set(true, forKey: "isLoggedIn")
        isLoggedIn = true
        path = NavigationPath()
    }

    func logout() {
        SessionStore.shared.clearSession()
        UserDefaults.standard.set(false, forKey: "isLoggedIn")
        isLoggedIn = false
        path = NavigationPath()
    }
}

