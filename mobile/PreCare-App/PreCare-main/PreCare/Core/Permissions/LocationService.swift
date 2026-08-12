import Foundation
import CoreLocation
import UserNotifications
import Combine

final class LocationService: NSObject, ObservableObject, CLLocationManagerDelegate {
    static let shared = LocationService()

    private let manager = CLLocationManager()
    private let geocoder = CLGeocoder()

    @Published var locationName: String = "Thandalam, Poonamallee, Chennai"
    @Published var nearestHospitalName: String = "Saveetha Medical College & Hospital (~0.1 km away)"
    @Published var doctorOnCall: String = "Dr. S. Lakshmi, MD (Available now)"
    @Published var ambulanceETA: String = "Available (ETA: 4 mins)"
    @Published var currentCoordinate: CLLocationCoordinate2D? = CLLocationCoordinate2D(latitude: 13.0286, longitude: 80.0164)
    @Published var nearbyDoctors: [Doctor] = Doctor.sampleDoctors

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
        manager.requestWhenInUseAuthorization()
        manager.startUpdatingLocation()
        recalculateHospitalDistances(coordinate: currentCoordinate)
    }

    func requestLocationPermission() {
        manager.requestWhenInUseAuthorization()
        manager.startUpdatingLocation()
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let loc = locations.last else { return }
        currentCoordinate = loc.coordinate

        recalculateHospitalDistances(coordinate: loc.coordinate)

        geocoder.reverseGeocodeLocation(loc) { [weak self] placemarks, error in
            guard let self = self, let place = placemarks?.first else { return }
            let city = place.locality ?? place.subLocality ?? place.name ?? "Current Location"
            let state = place.administrativeArea ?? ""
            let country = place.isoCountryCode ?? "IN"
            
            DispatchQueue.main.async {
                let resolved = state.isEmpty ? "\(city), \(country)" : "\(city), \(state)"
                self.locationName = resolved
            }
        }
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("Location manager error: \(error.localizedDescription)")
    }

    /// Calculates physical distance in kilometers using the Haversine formula
    func calculateDistanceKm(from: CLLocationCoordinate2D, toLat: Double, toLon: Double) -> Double {
        let lat1 = from.latitude * .pi / 180.0
        let lon1 = from.longitude * .pi / 180.0
        let lat2 = toLat * .pi / 180.0
        let lon2 = toLon * .pi / 180.0
        
        let dLat = lat2 - lat1
        let dLon = lon2 - lon1
        
        let a = sin(dLat / 2.0) * sin(dLat / 2.0) + cos(lat1) * cos(lat2) * sin(dLon / 2.0) * sin(dLon / 2.0)
        let c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a))
        let r = 6371.0
        return (r * c * 10).rounded() / 10.0
    }

    /// Constructs direct Google Maps turn-by-turn driving navigation URL
    func googleMapsDirectionsUrl(destinationLat: Double, destinationLon: Double) -> URL? {
        let originParam: String
        if let current = currentCoordinate {
            originParam = "origin=\(current.latitude),\(current.longitude)&"
        } else {
            originParam = ""
        }
        let urlString = "https://www.google.com/maps/dir/?api=1&\(originParam)destination=\(destinationLat),\(destinationLon)&travelmode=driving"
        return URL(string: urlString)
    }

    private func recalculateHospitalDistances(coordinate: CLLocationCoordinate2D?) {
        var updated = Doctor.sampleDoctors
        if let coord = coordinate {
            for i in 0..<updated.count {
                let dist = calculateDistanceKm(from: coord, toLat: updated[i].latitude, toLon: updated[i].longitude)
                updated[i].distanceKm = dist
                updated[i].mapsUrl = googleMapsDirectionsUrl(destinationLat: updated[i].latitude, destinationLon: updated[i].longitude)?.absoluteString
            }
            updated.sort { ($0.distanceKm ?? 9999) < ($1.distanceKm ?? 9999) }
        }

        if !updated.isEmpty {
            updated[0].aiRecommended = true
            updated[0].isClosest = true
            let dist = updated[0].distanceKm ?? 0.1
            updated[0].aiReason = "Closest verified maternity hospital to your current location (\(dist) km away)."
            
            DispatchQueue.main.async {
                self.nearbyDoctors = updated
                self.nearestHospitalName = "\(updated[0].name) (~\(dist) km away)"
                self.doctorOnCall = "\(updated[0].doctorName) (Available now)"
                self.ambulanceETA = "Available (ETA: \(max(3, Int(dist * 2.5))) mins)"
            }
        }
    }
}

