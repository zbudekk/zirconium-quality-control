# qc - stanowisko kontroli cyrkonii

Program stanowiska ze skanerem laboratoryjnym 3D we frezowni cyrkonii laboratorium protetycznego.
Wieczorem skanuje plytke z pracami w stanie zielonym, naklada kazda prace na jej projekt STL i oznacza
ukruszenia brzegow, zanim prace trafia do pieca. Rano z tego samego rodzaju skanu rozpoznaje, do
ktorego zlecenia (kuwety) nalezy kazda spieczona praca, a ramka swietlna z matryca LED podswietla
gniazda biezacej kuwety. Zlecenia, ktorych wszystkie punkty wyszly z pieca, program sam odhacza w
firmowym Excelu (zielone pole w kolumnie B) z logiem kazdej zmiany.

Repo zawiera program na laptopie (Python), program ramki na Raspberry Pi, modele plytek z ukladem
gniazd, testy na danych syntetycznych i narzedzia. Plan wdrozenia: "Stanowisko kontroli cyrkonii - plan
wdrozenia v2" (26.10.2026), poza repo.
