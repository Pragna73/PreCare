//
//  BookDoctorView.swift
//  PreCare
//

import SwiftUI

struct AppointmentDateOption: Identifiable {
    let id: Int
    let date: Date
    let title: String
    let subtitle: String
    let fullDisplay: String
}

struct BookDoctorView: View {
    @ObservedObject private var locationService = LocationService.shared

    @State private var selectedDoctor: Doctor? = nil
    @State private var availableDates: [AppointmentDateOption] = []
    @State private var selectedDateIndex: Int = 0
    @State private var availableSlots: [String] = []
    @State private var selectedSlot: String = "09:00 AM - 09:45 AM"
    @State private var showConfirmation = false
    @State private var isBooking = false

    var body: some View {
        ScrollView(showsIndicators: false) {
            VStack(spacing: 20) {

                // MARK: - AI Recommendation & Location Banner
                VStack(alignment: .leading, spacing: 8) {
                    HStack(spacing: 6) {
                        Image(systemName: "sparkles")
                            .foregroundColor(Color(hex: "#FF2D6F"))
                        Text("AI Smart Recommendation")
                            .font(.headline)
                            .foregroundColor(Color(hex: "#FF2D6F"))
                    }

                    Text("Based on your report analysis and detected GPS location (\(locationService.locationName)), we recommend consulting an accredited obstetrician at \(locationService.nearestHospitalName).")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding()
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color(hex: "#FF2D6F").opacity(0.08))
                .cornerRadius(16)

                // MARK: - Select Date (Live Date Calculation)
                VStack(alignment: .leading, spacing: 10) {
                    HStack {
                        Text("Select Appointment Date")
                            .font(.headline)
                        Spacer()
                        Text("Live Schedule")
                            .font(.caption)
                            .foregroundColor(.green)
                    }

                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 10) {
                            ForEach(0..<availableDates.count, id: \.self) { idx in
                                Button {
                                    selectedDateIndex = idx
                                    updateSlotsForSelectedDate()
                                } label: {
                                    VStack(spacing: 4) {
                                        Text(availableDates[idx].title)
                                            .font(.system(size: 13, weight: .bold))
                                        Text(availableDates[idx].subtitle)
                                            .font(.system(size: 11))
                                    }
                                    .foregroundColor(selectedDateIndex == idx ? .white : .primary)
                                    .padding(.vertical, 10)
                                    .padding(.horizontal, 14)
                                    .background(
                                        RoundedRectangle(cornerRadius: 12)
                                            .fill(selectedDateIndex == idx ? Color(hex: "#FF2D6F") : Color(.secondarySystemGroupedBackground))
                                    )
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 12)
                                            .stroke(selectedDateIndex == idx ? Color.clear : Color.gray.opacity(0.2), lineWidth: 1)
                                    )
                                }
                            }
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                // MARK: - Select Time Slot
                VStack(alignment: .leading, spacing: 10) {
                    Text("Select Time Slot")
                        .font(.headline)

                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
                        ForEach(availableSlots, id: \.self) { slot in
                            Button {
                                selectedSlot = slot
                            } label: {
                                HStack(spacing: 6) {
                                    Image(systemName: "clock")
                                        .font(.caption)
                                    Text(slot)
                                        .font(.system(size: 12, weight: .medium))
                                        .lineLimit(1)
                                        .minimumScaleFactor(0.8)
                                }
                                .foregroundColor(selectedSlot == slot ? .white : .primary)
                                .padding(.vertical, 12)
                                .padding(.horizontal, 6)
                                .frame(maxWidth: .infinity)
                                .background(
                                    RoundedRectangle(cornerRadius: 12)
                                        .fill(selectedSlot == slot ? Color(hex: "#FF2D6F") : Color(.secondarySystemGroupedBackground))
                                    )
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(selectedSlot == slot ? Color.clear : Color.gray.opacity(0.2), lineWidth: 1)
                                )
                            }
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                // MARK: - Verified Regional Hospitals (Sorted by Proximity)
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Text("Nearby Hospitals & Specialists")
                            .font(.title3)
                            .fontWeight(.bold)
                        Spacer()
                        Text("📍 Sorted by Proximity")
                            .font(.caption)
                            .foregroundColor(.blue)
                    }

                    ForEach(locationService.nearbyDoctors) { doctor in
                        DoctorCard(
                            doctor: doctor,
                            isSelected: selectedDoctor?.id == doctor.id,
                            onSelect: {
                                selectedDoctor = doctor
                            }
                        )
                    }
                }

                // MARK: - Book Button
                PrimaryButton(
                    title: selectedDoctor == nil
                        ? "Select a Hospital / Doctor"
                        : "Book Consultation with \(selectedDoctor!.doctorName)"
                ) {
                    isBooking = true
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                        isBooking = false
                        showConfirmation = true
                    }
                }
                .disabled(selectedDoctor == nil || isBooking)
                .opacity(selectedDoctor == nil ? 0.6 : 1)

                Spacer(minLength: 20)
            }
            .padding()
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle("Book Doctor")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            setupLiveDatesAndSlots()
            if selectedDoctor == nil {
                selectedDoctor = locationService.nearbyDoctors.first
            }
        }
        .navigationDestination(isPresented: $showConfirmation) {
            if let doctor = selectedDoctor {
                let chosenDateString = availableDates.indices.contains(selectedDateIndex)
                    ? availableDates[selectedDateIndex].fullDisplay
                    : "Tomorrow"

                AppointmentConfirmationView(
                    doctor: doctor,
                    appointmentDate: chosenDateString,
                    appointmentTime: selectedSlot
                )
            }
        }
    }

    private func setupLiveDatesAndSlots() {
        let calendar = Calendar.current
        let now = Date()
        let hour = calendar.component(.hour, from: now)

        let formatter = DateFormatter()
        formatter.dateFormat = "MMM d, yyyy"

        let dayFormatter = DateFormatter()
        dayFormatter.dateFormat = "EEEE"

        var options: [AppointmentDateOption] = []
        let startOffset = (hour >= 18) ? 1 : 0

        for i in startOffset..<(startOffset + 5) {
            guard let date = calendar.date(byAdding: .day, value: i, to: now) else { continue }
            let title: String
            if calendar.isDateInToday(date) {
                title = "Today"
            } else if calendar.isDateInTomorrow(date) {
                title = "Tomorrow"
            } else {
                title = dayFormatter.string(from: date)
            }
            let sub = formatter.string(from: date)
            options.append(AppointmentDateOption(
                id: i,
                date: date,
                title: title,
                subtitle: sub,
                fullDisplay: "\(title), \(sub)"
            ))
        }

        self.availableDates = options
        self.selectedDateIndex = 0
        updateSlotsForSelectedDate()
    }

    private func updateSlotsForSelectedDate() {
        guard availableDates.indices.contains(selectedDateIndex) else { return }
        let chosenDate = availableDates[selectedDateIndex].date
        let calendar = Calendar.current
        let now = Date()
        let isToday = calendar.isDateInToday(chosenDate)
        let currentHour = calendar.component(.hour, from: now)

        let allSlots: [(hour: Int, label: String)] = [
            (9, "09:00 AM - 09:45 AM"),
            (10, "10:00 AM - 10:45 AM"),
            (11, "11:30 AM - 12:15 PM"),
            (14, "02:30 PM - 03:15 PM"),
            (16, "04:30 PM - 05:15 PM"),
            (18, "06:00 PM - 06:45 PM")
        ]

        if isToday {
            let future = allSlots.filter { $0.hour > currentHour + 1 }.map { $0.label }
            if !future.isEmpty {
                self.availableSlots = future
            } else {
                self.availableSlots = ["Emergency On-Call Slot"]
            }
        } else {
            self.availableSlots = allSlots.map { $0.label }
        }

        if let first = availableSlots.first {
            self.selectedSlot = first
        }
    }
}
