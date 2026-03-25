# OpenAQ Classification Reference

- Status: Reference detail for slice 1 implementation
- Date: 2026-03-18
- Scope: Preserve the OpenAQ-specific background and examples that informed the air-quality silver classification rules.

## Current Code Paths

- `OpenAQCollector._get_sensors_country()` fetches location metadata from `client.locations.list(...)`.
- That code already captures `provider_name` and `owner_name`.
- It also stores a rough `sensor_grade` value, but that field is currently just the first instrument name from the `instruments` list, not a final trusted grade label.
- `src/data_processors/openaq_realtime_client.py` already merges this metadata back onto realtime measurements before saving output.

## Live Confirmation From The OpenAQ API

Confirmed on 2026-03-18 from a Thailand/Laos sample of 783 locations:

- metadata fields `provider_name`, `owner_name`, and `instruments` were present and usable
- observed top providers:
  - `AirGradient` (480)
  - `Air4Thai` (259)
  - `Thailand` (33)
  - `Clarity` (3)
  - `HabitatMap` (1)
- observed top instruments:
  - `Unknown AirGradient Sensor` (427)
  - `Government Monitor` (295)
  - multiple specific `AirGradient ...` instrument names
  - `Clarity Sensor`
  - `HabitatMap Sensor`

## Reference-Grade Fixtures

- `provider_name = Air4Thai`, `owner_name = Unknown Governmental Organization`, `instruments = ["Government Monitor"]`
- `provider_name = Thailand`, `owner_name = Unknown Governmental Organization`, `instruments = ["Government Monitor"]`

## Low-Cost Fixtures

- `provider_name = AirGradient`, `instruments` containing `Unknown AirGradient Sensor`
- `provider_name = AirGradient`, `instruments` containing named `AirGradient ...` devices
- `provider_name = Clarity`, `instruments = ["Clarity Sensor"]`
- `provider_name = HabitatMap`, `instruments = ["HabitatMap Sensor"]`

## Important Non-Rules

- do not use `provider_name = Thailand` by itself as a reference-grade rule
- do not use `owner_name = Unknown Governmental Organization` by itself as a reference-grade rule
