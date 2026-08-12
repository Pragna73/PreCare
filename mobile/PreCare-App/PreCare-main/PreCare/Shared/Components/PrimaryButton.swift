import SwiftUI

struct PrimaryButton: View {

    let title: String
    var icon: String? = nil
    var color: Color = Color(hex: "#FF2D6F")
    let action: () -> Void

    init(
        title: String,
        icon: String? = nil,
        color: Color = Color(hex: "#FF2D6F"),
        action: @escaping () -> Void
    ) {
        self.title = title
        self.icon = icon
        self.color = color
        self.action = action
    }

    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                Spacer()
                if let icon {
                    Image(systemName: icon)
                        .font(.system(size: 16, weight: .bold))
                }
                Text(title)
                    .font(.system(size: 16, weight: .semibold))
                Spacer()
            }
            .foregroundColor(.white)
            .frame(height: 54)
            .background(color)
            .cornerRadius(16)
        }
    }
}

