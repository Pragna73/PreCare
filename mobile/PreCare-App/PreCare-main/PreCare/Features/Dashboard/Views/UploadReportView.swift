import SwiftUI
import UniformTypeIdentifiers
import UIKit

struct UploadReportView: View {
    @StateObject private var vm = DashboardViewModel()

    @State private var selectedFileURL: URL?
    @State private var showFilePicker = false
    @State private var showImagePicker = false
    @State private var imagePickerSource: UIImagePickerController.SourceType = .photoLibrary
    @State private var showUploadOptions = false
    @State private var navigateToResult = false

    private var allowedTypes: [UTType] {
        var types: [UTType] = [.pdf, .plainText, .image]
        if let docx = UTType(filenameExtension: "docx") {
            types.append(docx)
        }
        if let doc = UTType(filenameExtension: "doc") {
            types.append(doc)
        }
        return types
    }

    var body: some View {
        ScrollView(showsIndicators: false) {
            VStack(spacing: 16) {
                CardView {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack(spacing: 6) {
                            Image(systemName: "cross.case.fill")
                                .foregroundColor(Color(hex: "#FF2D6F"))
                            Text("Upload Pregnancy Report")
                                .font(.title3)
                                .fontWeight(.bold)
                        }
                        Text("Upload maternal health lab tests, ultrasound scans, or prenatal records (DOCX, PDF, Images).")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }

                CardView {
                    VStack(spacing: 14) {
                        Image(systemName: "doc.badge.plus")
                            .font(.system(size: 40))
                            .foregroundColor(Color(hex: "#FF2D6F"))

                        VStack(spacing: 4) {
                            Text(selectedFileURL?.lastPathComponent ?? "Tap to choose report file")
                                .font(.system(size: 15, weight: .semibold))
                                .foregroundColor(.primary)
                                .multilineTextAlignment(.center)

                            Text("Supported: DOCX, PDF, PNG, JPG, JPEG")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }

                        if selectedFileURL != nil {
                            HStack(spacing: 6) {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.green)
                                Text("File Selected Ready for Analysis")
                                    .font(.caption)
                                    .foregroundColor(.green)
                            }
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                }
                .onTapGesture { showUploadOptions = true }

                if vm.isLoading {
                    VStack(spacing: 8) {
                        ProgressView("Analyzing pregnancy indicators & vitals...")
                            .frame(maxWidth: .infinity)
                        Text("Checking BP, Hemoglobin, Glucose, FHR & Preeclampsia markers")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color(.secondarySystemGroupedBackground))
                    .cornerRadius(12)
                }

                PrimaryButton(title: vm.isLoading ? "Analyzing Report..." : "Upload & Analyze") {
                    startUpload()
                }
                .disabled(selectedFileURL == nil || vm.isLoading)
                .opacity(selectedFileURL == nil ? 0.65 : 1)

                if let errorMessage = vm.errorMessage {
                    VStack(alignment: .leading, spacing: 6) {
                        HStack(spacing: 6) {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(.red)
                            Text("Document Not Accepted")
                                .font(.headline)
                                .foregroundColor(.red)
                        }
                        Text(errorMessage)
                            .font(.footnote)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.red.opacity(0.08))
                    .cornerRadius(12)
                }
            }
            .padding()
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle("Upload Report")
        .navigationBarTitleDisplayMode(.inline)
        .navigationDestination(isPresented: $navigateToResult) {
            AnalysisResultView(severity: vm.latestSeverity, report: vm.latestReport)
        }
        .fileImporter(
            isPresented: $showFilePicker,
            allowedContentTypes: allowedTypes
        ) { result in
            if case .success(let url) = result {
                selectedFileURL = url
            }
        }
        .sheet(isPresented: $showImagePicker) {
            ImagePicker(sourceType: imagePickerSource) { image in
                if let image {
                    selectedFileURL = saveImageToTemporaryFile(image: image)
                }
            }
        }
        .confirmationDialog("Upload Report", isPresented: $showUploadOptions, titleVisibility: .visible) {
            Button("Capture with Camera") {
                guard UIImagePickerController.isSourceTypeAvailable(.camera) else {
                    vm.errorMessage = "Camera is not available on this device."
                    return
                }
                imagePickerSource = .camera
                showImagePicker = true
            }
            Button("Pick from Photos") {
                imagePickerSource = .photoLibrary
                showImagePicker = true
            }
            Button("Pick PDF / DOCX / File") { showFilePicker = true }
            Button("Cancel", role: .cancel) {}
        }
    }

    private func startUpload() {
        guard let selectedFileURL else { return }

        // Client-side quick check for obvious non-medical filenames
        let lowerName = selectedFileURL.lastPathComponent.lowercased()
        let nonMedicalPatterns = ["resume", "cv", "invoice", "receipt", "assignment", "homework", "bank", "statement", "screenshot", "wallpaper", "id_card", "passport", "driving_license", "aadhaar", "pan_card"]
        for pat in nonMedicalPatterns {
            if lowerName.contains(pat) {
                vm.errorMessage = "Invalid Document: '\(selectedFileURL.lastPathComponent)' does not contain recognized pregnancy or maternal health parameters. Please upload an actual maternal health lab report, blood test, or ultrasound scan."
                return
            }
        }

        Task {
            let canAccess = selectedFileURL.startAccessingSecurityScopedResource()
            defer {
                if canAccess {
                    selectedFileURL.stopAccessingSecurityScopedResource()
                }
            }
            let success = await vm.uploadReport(fileURL: selectedFileURL)
            if success {
                navigateToResult = true
            }
        }
    }

    private func saveImageToTemporaryFile(image: UIImage) -> URL? {
        guard let data = image.jpegData(compressionQuality: 0.9) else { return nil }
        let tempDir = FileManager.default.temporaryDirectory
        let fileURL = tempDir.appendingPathComponent("captured_pregnancy_report_\(UUID().uuidString).jpg")
        do {
            try data.write(to: fileURL)
            return fileURL
        } catch {
            vm.errorMessage = error.localizedDescription
            return nil
        }
    }

    private func riskColor(_ risk: String?) -> Color {
        switch (risk ?? "").uppercased() {
        case "GOOD", "FINE", "SAFE", "LOW":
            return .green
        case "WARNING", "MODERATE", "MEDIUM":
            return .orange
        case "DANGER", "HIGH", "CRITICAL":
            return .red
        default:
            return .gray
        }
    }
}
