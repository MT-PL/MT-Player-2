# Wymagania produktu (MTV — Modular Timeline Viewer)

## Cel i scenariusze użycia
- Główny cel: odtwarzanie i analiza materiału z monitoringu CCTV zgrywanego z obiektu do centrali; wsparcie dochodzeń (kradzieże, wypadki, analiza pracy).  
- Tryb pracy na start: pojedyncza kamera, z planem rozbudowy do multi‑view.  
- Oś czasu globalna: aplikacja wyznacza chronologię na podstawie plików w katalogu, od najnowszego do najstarszego.  
- Krytyczne akcje: szybkie przewijanie, „go to datetime”, następna klatka, wybór klipu.  

## System i dystrybucja
- Docelowy OS: Windows (tylko).  
- Dystrybucja: portable ZIP.  
- Praca offline po instalacji.  
- Zakładany sprzęt: od laptopa Intel i5‑10210U / 16 GB RAM / iGPU do stacji z Intel Core Ultra 7 265 + RTX A1000 / 32 GB RAM.  

## Format nagrań i kodeki
- Kontenery: „wszystkie możliwe” (różne typy i rozszerzenia).  
- Kodeki: H.264/H.265.  
- Audio: brak (można ignorować).  
- Segmentacja plików: różna — aplikacja sama weryfikuje i dopasowuje.  

## Metadane czasu i kamer
- Źródło prawdy: nazwa pliku (priorytet).  
- Strefa czasowa: Europe/Warsaw.  
- Obsługa DST: preferowana.  
- Aplikacja musi sama weryfikować poprawność i spójność czasu.  

## UI/UX (MVP)
- Ekran startowy: lista kamer + lista klipów + player + oś czasu + statusy.  
- Skróty klawiaturowe: spacja (play/pause), strzałki (seek), zmiana kamery itp.  
- Pasek postępu skanowania + raport pominiętych — wymagane w MVP.  
- Wygląd: „ładne i wygładzone”.  

## Funkcje dowodowe
- Snapshot/eksport: „pakiet dowodowy” (czas, kamera, hash pliku, log).  
- Eksport klipu: przycinanie i zapis fragmentu.  
- Log audytowy: wymagany.  

## Skala i wydajność
- Liczba plików: 1–5000.  
- Struktura katalogów: płaska lub zagnieżdżona.  
- Cache skanowania (np. SQLite + OCR) — wymagany.  

## Ryzyka i zależności
- Dopuszczalne FFmpeg/ffprobe jako zależności (z możliwością rozbudowy).  
- Silnik odtwarzania: „najlepszy jaki może być” (praktycznie, byle działało).  
- Wsparcie dla „dziwnych” plików producenta: wymagane.  

## Uwagi organizacyjne
- Architektura modułowa („kontenerowa”) ułatwiająca rozbudowę.  
- Przy kolejnych iteracjach kodu zawsze wskazujemy dokładne miejsca zmian (gdzie dokleić/zmienić).  
- Nazwa aplikacji: MTV.  
