//
//  EmergencyTrackingView.swift
//  PreCare
//
//

import SwiftUI
import MapKit

struct EmergencyTrackingView: View {

    @StateObject private var vm = EmergencyViewModel()
    @ObservedObject private var locationService = LocationService.shared

    // MARK: - Map State
    @State private var region = MKCoordinateRegion(
        center: CLLocationCoordinate2D(
            latitude: 13.0827,   // Chennai / Tamil Nadu Belt
            longitude: 80.2707
        ),
        span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
    )

    // Live ambulance location
    private var ambulanceCoordinate: CLLocationCoordinate2D {
        if let current = locationService.currentCoordinate {
            return CLLocationCoordinate2D(latitude: current.latitude + 0.005, longitude: current.longitude + 0.005)
        }
        return CLLocationCoordinate2D(latitude: 13.0850, longitude: 80.2730)
    }

    private func callFamily() {
        let rawNumber = SessionStore.shared.emergencyContact.isEmpty ? "9885757159" : SessionStore.shared.emergencyContact
        let clean = rawNumber.filter { "0123456789+".contains($0) }
        if let url = URL(string: "tel://\(clean)") {
            UIApplication.shared.open(url)
        }
    }

    var body: some View {
        VStack(spacing: 24) {

            // MARK: - ETA
            VStack(spacing: 6) {
                Text("\(vm.etaMinutes) min")
                    .font(.system(size: 42, weight: .bold))
                    .foregroundColor(.green)

                Text("Ambulance arriving soon to \(locationService.locationName)")
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }

            // MARK: - LIVE MAP
            Map(coordinateRegion: $region, annotationItems: [
                MapPinItem(
                    coordinate: ambulanceCoordinate,
                    title: "Ambulance"
                )
            ]) { item in
                MapMarker(coordinate: item.coordinate, tint: .green)
            }
            .frame(height: 200)
            .cornerRadius(16)
            .overlay(
                HStack {
                    Image(systemName: "location.fill")
                        .foregroundColor(.green)
                    Text(vm.distance)
                        .font(.caption)
                        .foregroundColor(.green)
                }
                .padding(8),
                alignment: .bottomLeading
            )

            // MARK: - Live Status
            VStack(spacing: 16) {

                EmergencyStatusRow(
                    icon: "cross.case.fill",
                    title: "Paramedics",
                    subtitle: "En Route • \(vm.etaMinutes) min",
                    confirmed: true
                )

                EmergencyStatusRow(
                    icon: "cross.fill",
                    title: "Assigned Hospital",
                    subtitle: locationService.nearestHospitalName,
                    confirmed: true
                )

                EmergencyStatusRow(
                    icon: "person.2.fill",
                    title: "Emergency Family Contact",
                    subtitle: SessionStore.shared.emergencyContact.isEmpty ? "Alerted via SMS" : "\(SessionStore.shared.emergencyContact) • Alerted via SMS",
                    confirmed: true
                )
            }

            Spacer()

            // MARK: - Call Buttons
            PrimaryButton(title: "Call Emergency Contact (\(SessionStore.shared.emergencyContact.isEmpty ? "Family" : SessionStore.shared.emergencyContact))", color: .green) {
                callFamily()
            }

            Button {
                if let url = URL(string: "tel://108") {
                    UIApplication.shared.open(url)
                }
            } label: {
                Text("🚨 Call 108 / Emergency Ambulance Service")
                    .foregroundColor(.red)
                    .font(.subheadline)
                    .fontWeight(.bold)
            }

            Spacer(minLength: 20)
        }
        .padding()
        .navigationTitle("Emergency Status")
        .navigationBarTitleDisplayMode(.inline)
    }
}
