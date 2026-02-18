import streamlit as st
import pandas as pd
import os, io, json, base64
import streamlit.components.v1 as components

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ======================================================
# KONFIGURASI
# ======================================================
DATA_DIR = "data/senarai_nama"

TAHUN_OPTIONS = ["2 DVM", "1 DVM", "2 SVM", "1 SVM", "OPP"]
KELAS_BIASA = ["BAK", "BPM", "HSK", "HBP", "KMK", "KPD"]
KELAS_OPP = ["4 OPP", "5 OPP"]

KOHORT_OPTIONS = list(range(2025, 2050))

KAEDAH_OPTIONS = ["SILA PILIH", "Tunai", "Bank"]
CSV_COLUMNS = [
    "Nama",
    "Bayaran 1", "Tarikh 1",
    "Bayaran 2", "Tarikh 2",
    "Bayaran 3", "Tarikh 3",
    "Jumlah",
    "Kaedah"
]

# ======================================================
# SENARAI NAMA PELAJAR IKUT KELAS
# ======================================================
NAMA_PELAJAR_KELAS = {

# ======================================================
# 2 DVM (SEMUA KELAS)
# ======================================================
"2 DVM BAK": [
    "SILA PILIH",
    "AQIL ISKANDAR BIN AZRUL ADNAN",
    "DALIA ADNI BINTI MOHD SAMSURANI @ MOHD SAHARANIN",
    "FARIZAH IRDINA BINTI MOHD FARIZAD",
    "HAIDA BATRISYIA BINTI HAIDA IRWAN",
    "HUMAIRA BINTI ZAINAL",
    "MUHAMMAD NIZAMUDDIN BIN MOHD KADRI",
    "MUHAMMAD SHAHRUL IQBAL BIN ZAINUDIN",
    "NUR AFIFAH NAJIHAH BINTI MUHAMAD JAMMARI",
    "NUR ANATI HUSNA BINTI MOHD FAUZI",
    "NUR ARISYA SUFFIYA BINTI MUHD NUZZI",
    "NUR ATIQAH SYAHIRAH BINTI BAKTIAR",
    "NUR ELLYANA ASYURA BINTI MOHAMED SAILAN",
    "NUR FARAHNEZZAN BINTI MOHD NASIR",
    "NUR FARIHA MOHD KAIL",
    "NUR FILDZAH IRDINA BINTI RAZALI",
    "NUR HIDAYAH BINTI AZLI",
    "NURAFIFAH ADAWIYAH BINTI AMRAN",
    "NURBATRISYIA BINTI MOHD NADZARI",
    "NURUL IZZAH BINTI RIDUAN",
    "RAJA NOR DAIYANA BINTI RAJA UMAR",
    "SHIMA QIESTINA BINTI MUHAMMAD ALI",
    "WAN NUR SOFEA BATRISYIA BINTI WAN AZUADI",
    "ZAIRIL IRIFAN BIN ZAHRIZAN",
],

"2 DVM BPM": [
    "SILA PILIH",
    "AIN KHAYATI BINTI AHMAD FUADI",
    "AIN UMAIRAH SYUQAIRAH BINTI MOHD AZRI",
    "AMIRA AZWIEN BINTI AIROLASMAWI",
    "HABIB NUSAIKI BIN MOHD ISMAWI",
    "HASVADIA BINTI MOHD HANAFI",
    "INDAH NURSAJ'DAH BINTI NAHARANUAR",
    "MASHA AMIRAH BINTI MAZLAN",
    "MIRZA UBAIDAH BINTI MOHD SAPUAN",
    "MUHAMMAD AFIF FARHAN BIN ANIZAM",
    "DANIAL AIMAN BIN ABDULLAH",
    "MUHAMMAD IRFAN DANIAL BIN MADZLI TASRIN",
    "MUHAMMAD NOR HAIZAD MUHAMMAD ZULKAFRY",
    "MUHAMMAD SHAH AIMAN BIN SHAH RIDZAL",
    "NUR AISYAH DAMIA BINTI ASAN ALWI",
    "NUR FARAHIYAH ELLEYSA BINTI MOHD RIZAL FAHMI",
    "NUR FARZANA BINTI MOHD AZRAN",
    "NUR MYA UMAIRAH BINTI AHMAD ROZMAN",
    "NURAIN FARISYA BINTI NAZRI",
    "NURAMIRA AIN NAZWIN BINTI OSMAN",
    "NURNAILI DALILA BINTI MOHD RAZI",
    "NURUL ASYIQIN BINTI SAIFUL AZWAN",
    "SHARIFATUL ATIQAH BINTI BASERI",
    "SUFI IQLIMA BINTI AKMAL HAKIM",
    "NUR HANI HAZIRAH BINTI HAMDAN(DAFTAR 2023)",
    "ARIANI FARINNI BINTI MOHD FARZELIN",
    "NUR AINA NADIRAH BINTI MOHAMAD NOR AZALI",
],

"2 DVM HBP": [
    "SILA PILIH",
    "ADAM DARIMI BIN ROZMAN",
    "ADDINA NURADRIANA BINTI ADRIAN",
    "ADRIANA RASHADAH BINTI FAIRUL NIZAM",
    "BALQISH BATRISYA BINTI AL-FIRO",
    "HANISA BINTI ABDUL HALIM",
    "INAS SHAKIRAH BINTI RIDHUAN",
    "MUHAMMAD ADAM ZAFRAN BIN MOHD AZMY",
    "MUHAMMAD ADAM ZUHDI BIN IBRAHIM",
    "MUHAMMAD AIMAN HAKIM BIN MOHD AZAD",
    "MUHAMMAD HAIKAL BIN MOHAMAD MISWADI",
    "MUHAMMAD HAZZIQ ZAHRAN BIN HAMIRUN",
    "NADINE NASREEN BINTI YUSSAINY",
    "NUREEN HANNAH BINTI ARISANUAR",
    "NURIN BASYIRAH BINTI ZULKIFLI",
    "PUTERI FARISHA NAJIHAH BINTI NOOR ZAMRI",
    "SITI UMAIRAH BINTI MOHAMED MAZLAN",
],

"2 DVM HSK": [
    "SILA PILIH",
    "AISH HAIKAL BIN ASHFI",
    "AQIF EZAIRY BIN MOHD.RUSDI",
    "MUHAMMAD AMAR BIN MOHD FHAIZAL",
    "MUHAMMAD AQIF MOHD HAZWARDI",
    "MUHAMMAD AQIL DANIAL BIN ABDULLAH",
    "NUR AMALINA BINTI MOHD RUSLI",
    "NUR FARAH SYAZANA BINTI AB KADIR",
    "NUR PUTRI SARAH YASMIN BINTI NOOR AZLAN",
    "NURAISYA BINTI MOHAMAD HAFIZ",
    "NURIN SHIFA UZMA BINTI MUSTAFA",
    "NURUL ASYIKIN BINTI MOHD TAJURI",
    "SYAMIL AYMAN HAQIMI BIN SAHRUL PAHMI",
    "HUDDA AMIRUL AFDLIN BIN HUDDA FIRDAUS AZIZI",
    "SITI NURULAKMA BINTI AHMAD LATHPI",
    "SITI MARYAM UMAIMAH BINTI AZMAN",
],

"2 DVM KMK": [
    "SILA PILIH",
    "ADAM BIN AIDY",
    "ADAM ZULKARNAIN BIN SYAMSUL HAFIZ",
    "ALYA' FAIQAH ATHIRAH BINTI MOHD FAIZUL",
    "ARIENA FARISHA BINTI ABDUL MURAD",
    "AVRIL ILHAM BIN HASNOL HISHAM",
    "FATIN NURHUSNA BINTI ZAHARIN",
    "FATMA AZZAHRA BINTI ZAIDI",
    "HANI SYAKIRAH BINTI ABD HALID",
    "HANIN AMANI BINTI JASNI",
    "IRDINA SUFIAH BINTI MOHAMAD HASHIM",
    "JAMALUDDIN HAKIMI",
    "MUHAMMAD FARIS BIN ZAFIRAN",
    "MUHAMMAD HAIKAL BIN NOOR AZRI",
    "MUHAMMAD IRFAN BIN HONEYSYAM",
    "MUHAMMAD NUR ADAM BIN HAIRUZAM",
    "MUHAMMAD NURADHAM BIN MOHD AYUB",
    "MUHAMMAD SOKHIPOL QAWIEM BIN SOKHIPOL AKMAM",
    "NUHA DAMIA BINTI ZAMZURI",
    "NUR AFRINA AMANI BINTI FAUZI",
    "NUR AIN ALISA BINTI MOHD IDRIS",
    "NUR ALESHA BINTI MOHD RIZAL",
    "NUR HAMIZAH BINTI HALIM",
    "NUR HAZIMAH BINTI HALIM",
    "NUR NADIAH BINTI NORZAILAN",
    "NUR QADEEJA BINTI AMRIZAL",
    "NUR SYAHZANANI ATIQAH BINTI SAZALIZAM",
    "NURDANIA ASYIQIN BINTI MOHD NORDIN",
    "NURELISA SHAFIYA BINTI MOHD ZAMRI",
    "BALQISH BINTI BUDIMAN",
],

"2 DVM KPD": [
    "SILA PILIH",
    "ADAM MUKHRIZ BIN MUHAMMAD JALIL SAYUTY",
    "AINNUR QISTINA PUTRI BINTI Q HISHAM",
    "ALIYA SAFIYYAH BINTI ZAMIL MARWAN",
    "AMI AFINA IZZATY BINTI AMIZAD",
    "AZHAN ADLI BIN MOHD BORHAN",
    "DANIAL IRFAN BIN ZAKARIA",
    "ERFAN BAGUS PRASETYO BIN NURAINI",
    "HAZWAN HAIKAL BIN HAIZAM IRWAN",
    "MUHAMAD IKBAL IMAN MOHD SUZUDI",
    "MUHAMAD MUIZZUDDIN BIN MOHD SUHAIMI",
    "MUHAMMAD ADDAM BIN BADROL",
    "MUHAMMAD IZZAT IKHMAL BIN MOHD IZAMIR",
    "NAZMI AIMAN BIN SAHREL",
    "NUR DINI FATIHAH BINTI ABDUL ISHAM",
    "NUR SYAFIZLEEN HAIZA BINTI NIZZAM",
    "NUR UMAIRAH NAFISAH BINTI NOR HASHIM",
    "NUR ZAHIRA BINTI AHMAD ZAHID",
    "NURSYIFAQ ALIEYA BINTI AHMAD AZRI",
    "SHAH ADAM BIN HUSSIN",
    "SYAZRIN HADRI BIN SHAHRUL NIZAM",
],

# ======================================================
# 1 DVM (SEMUA KELAS)
# ======================================================
"1 DVM BAK": [
    "SILA PILIH",
    "ADRUCE MIKHAIL BIN MOHD SIDEK",
    "AHMAD AQIL HARITH BIN MOHD AZLAN",
    "AHMED AQIL ADLI BIN AZMI",
    "AMIRAH ZULAIKHA BINTI ASRIZAN",
    "AMIRUL ARIF ASYRAF SOLIHIN BIN MOHD KHALID",
    "AMJAD AQIL BIN SULAIMAN",
    "AMYRAH HAQEESYA BINTI FAILSAL @ MOHD FAILSAL",
    "MOHAMMAD MUAWIYAH BIN SAMSUDIN",
    "NOORALYA BATRISYIA BINTI YUSSAIRY",
    "NUR ALYANADILA BINTI AMINURASHID",
    "NUR HUDA BINTI ABDULLAH",
    "NUR NASUHA BINTI HASMAN",
    "NUR WAHIDAH BINTI SHAMSUL ANUAR",
    "NUR'AINA BATRISYIA BINTI MOHAMAD YUSUF",
    "NURIN JAZLINA BINTI JAILANI",
    "QURRATU' AINI BINTI AHMAD TARMIZI",
    "SYARIFAH QISTINA BINTI SAYID ADNAN",
    "PUTRI ALYFA BATRISYIA BINTI MOHD TARMIZI",
    "NUR INTAN INSYIRAH BINTI AFINDI",
    "MOHAMMAD AQIL BIN MOHAMMAD NAIM",
    "NUR ANIS FARISHA BINTI MUHAMAD ROZI",
    "UNGKU DANISHARF DANIAL BIN UNGKU RIDZWAN",
    "BALQIS QASRINA BATRISYIA BINTI HAIDIL",
    "NUR AIN NAJIEHAH BINTI MOHD JOHARI",
    "MUHAMMAD FARHAN BIN NAZRUL NAIM",
    "NUR DAMIA LUTFIAH BINTI MOHD NAWAWI",
],

"1 DVM BPM": [
    "SILA PILIH",
    "AINANIS AZWATI BINTI MOHAMAD DISA",
    "MUHAMMAD DANIAL HAFIS BIN HAIRUL ADNAN",
    "NUR ELLYSYA ADRIN BINTI ROZAIDI",
    "NUR ARISA BATRISHA BINTI MOHD AZAM",
    "NUR AIRIEN AMANI BINTI NORIZUAN",
    "MYRA SAFFIYA BINTI MOHD MASRI",
    "NUR MAISARAH BINTI MOHD ZAILANI",
    "SITI AISYAH NABILAH BINTI ERWANYUS",
    "NYLA FAKHIRA BINTI MOHD ROSLI",
    "SITI NUR DAMIA BINTI MUHAMMAD LOQMAN",
    "MASYA DAMIA FATIHAH BINTI MIOR ZUNAIDI",
    "MUHAMMAD DINIEL IDZNI BIN MD SHAIFFUL",
    "NUR AMIRA HANI BINTI AZIZ",
    "MUMTAZ QISTINA BINTI MOHD EZHAM",
    "PUTERI NOR AQILAH ATHIRAH BINTI ALIAN SATAR",
    "NUR BATRISYIA SAFFIYA BINTI MOHD BADERUL KHAIZAM",
    "NURUL SYAQIRA BINTI YUSMAN",
    "MIRZA UMAIRAH BINTI MOHD SAPUAN",
    "NUR DAMIA BASIRAH BINTI SHAHRIN",
    "NURSHAHIDATUL EZREEN BINTI MOHD SUPIAN",
    "MUHAMMAD FAIQ MUQRI BIN ABD HALIM",
    "NURUL SYUHADA BINTI HAIRANI",
    "QASEH NUR ZAHARAH BINTI ABDULLAH",
    "MUHAMMAD AIRELL DANISH BIN ZAINAL",
    "DAYANG NUR AMALIN NATASYA BINTI MOHD NAZIR",
    "AIDA NABILAH BINTI ESTIHAR DURAE SUBHA",
    "ADHWA IZZATI SYAKIRAH BINTI SHAHIRUDIN",
    "NURUL HANAN LATIFAH BINTI MOHAMMAD AZRUL",
],

"1 DVM HBP": [
    "SILA PILIH",
    "AQILAH MURSYIDAH BINTI KHAHARUDDIN",
    "MUHAMMAD ARIQ BIN MOHAMMED KHAIRUL ZAMAN",
    "NIFAIL AFIF SHAH BIN SHAHRUL EZWAN",
    "NIK MOHD DANISH ASHRAF BIN ABDULLAH",
    "ANAS TIFTAZANI BIN KHAIRUL IZWAN",
    "MUHAMMAD AMEER IZZAT BIN AZMAN",
    "MUHAMMAD HARITH HAMMAM BIN MOHD ROFTEPI",
    "WAN MOHAMMAD HAZIQ BIN ZULKIFLI",
    "AUJI BATRISYIA BINTI MUHAMAD AKMAL",
    "NUR ALISA NADIA BINTI NOR AZMAN",
    "SHAFEENA ARISSA BINTI SHANIZUAN",
    "HANNAH MARISSA BINTI KAMARUDDIN",
    "AISHAH SOFIAH BINTI FADZLI",
    "SARAH AIN NAJWA BINTI NOORAINI",
    "NUR ALLISYA SOFEA BINTI HALIM",
    "MOHAMMAD AIRIL RAIS BIN MOHAMMAD ROIZZIDDIN",
    "NURUL FATHIN DAMIA BINTI MOHD HARPIZI",
    "ANIS ADRIEANA BINTI MOHD KHAIRIL ASHRAF",
    "NUR DAMIA INSYIRAH BINTI MOHD ZUKIFLI",
],

"1 DVM HSK": [
    "SILA PILIH",
    "FARIS ISKANDAR BIN MOHAMMAD ZAIDI",
    "MOHAMAD AQEEL BIN EL HEMRA",
    "MUHAMMAD ADWA ADHA BIN HASMADI",
    "MUHAMMAD HARITH AZIM BIN AZNAN",
    "NOOR AMMAR WAFIQ BIN NOORWARIDI",
    "NUR ALISSA NADIAH BINTI MOHD ASMADI",
    "NUR AQIELA DALIELA BINTI ROZAIDI",
    "NUR BATRISYIA BINTI AHMAD FADZIL",
    "NUR IMAN IZZATI BINTI ZULKEFLI",
    "NURFARISHA NAZULIA BINTI ZAMRI",
    "NURULAIN AFRINA BINTI ZULKARNAIN",
    "SHARIFAH NURUL INSYIRAH BINTI SYED NAZR",
    "SITI 'AISYAH BINTI ZUWAIRI",
    "SOFEA FATHIHAH BINTI SAHARUDDIN",
    "WAN KAMARUDDIN BIN WAN AZEMI",
    "MUHAMAD EMRAN HAQIMIE",
    "MUHAMMAD IRFAN FIRDAUS BIN CHE RANI",
],

"1 DVM KMK": [
    "SILA PILIH",
    "AHMADSHAH ANDY HAIKAL BIN MAKUNAGAN",
    "AMIRA ADDRIANA BINTI KHAIRUDDIN",
    "DHIYAA IRDINA A'ISYAH BINTI MOHAMAD AMIN",
    "DZHAFEERA BINTI ROJITAN",
    "FARAH NUR DAHLIA BINTI BORHAN",
    "HANNAH DHIYA BINTI FYTHULLAH",
    "MOHAMED MIKHAIL AYRA BIN MOHAMED RAZEEF",
    "MUHAMAD FARHAN BIN MOHD FADZL",
    "MUHAMMAD ALIFF BIN MOHD RAZEFF",
    "MUKHLIS BIN AZUANDI",
    "NAJLA IRDHEENA BINTI AHMED SYAM",
    "NAJLA SAFIYYAH BINTI ROSHIDI",
    "NUR AINUL QISTINA BINTI MOHD ZAINAL FITRI",
    "NUR ALEA SAFIYYAH BINTI MOHD ZULDIN HUSSEIN",
    "NUR BALQIS DAMIA BINTI MUHAMAD FAIZAL",
    "NUR HANNAH BINTI JAMAL YUSUFI",
    "NUR REANA AFIFAH BINTI M.AZMI",
    "NURADIBAH BINTI SHAHRUL NIZA",
    "NURAFIQAH NAJWA BINTI ABD LATIFF",
    "NURDAMIA QISTINA BINTI MUHAMMAD SABRI",
    "NURIN AMANI BINTI MD MAHADIR",
    "NURKYRA KHAISYAH BINTI KANADDI",
    "NURUL HIDAYAH BINTI ZUL HAMIZI",
    "SHAFIQAH NUR MUNIRAH BINTI HASSAN",
    "SITI AISHAH SOFEA BINTI MOHAMAD YAZID",
    "SITI NUR IZZATI BINTI ROSLIZAN",
    "SUMAYYAH BINTI SULAIMAN",
    "UMIE UMAYRA BINTI IKMAL HAKIM",
    "UMMU HAANIYAH ZAHRAH BINTI MUHAMED ROIHAN",
    "ZARITH SOFEA ADLIN BINTI ZAILANI",
    "ARIEF HUSSEIN",
],

"1 DVM KPD": [
    "SILA PILIH",
    "AINUL WARDINA BINTI IYUS",
    "ANNIQ DARWISY BIN AMRIN",
    "ARIFF AFZAN BIN ARSHAD",
    "AZZIZ AZIZI BIN ABDUL AZIZ",
    "HAZAR INSYIRAAH BINTI MOHD AZLI",
    "KHADIJAH HANUM BINTI MOHAMAD NIZAM",
    "MUHAMMAD AIDIL WAFIY BIN MOHD ADLI",
    "MUHAMMAD AQIF IMRAN BIN ADAM KARIM",
    "MUHAMMAD FARID BIN FADZLI HISHAM",
    "MUHAMMAD HAFIZUL AFHAM BIN MOHD ASRUL ARASHI",
    "MUHAMMAD HARITH BIN MOHAMAD MISWADI",
    "NUR AIMAN DINIE BIN MOHD FAHRURRAZI",
    "NUR ALYA QAUSAR BINTI AZHAR",
    "NUR DIYANA NABILA BINTI MADROZI",
    "NUR NAZLAH NAZIFA BINTI MOHD RIDZUAN",
    "PUTRI ELIEYRA BINTI JAMALUDIN",
    "RYAN MESSI BIN BENJY",
    "SHARIZAT BINTI HUSSIN",
    "TAIB RAAMIZ AAREZ BIN TAIB ZIAD",
    "TENGKU FATIMATUZZAHRA BINTI TENGKU MOHD UZAINI",
],

# ======================================================
# 2 SVM (SEMUA KELAS)
# ======================================================
"2 SVM BAK": [
    "SILA PILIH",
    "AHMAD HAIKAL IKHWAN BIN ALWI HAZRIN",
    "ALYAA INSYIRAH BINTI ADAM",
    "ALYAA NADZIRAH BINTI MOHD HAIRUL NIZAM",
    "AUFA QISTINA BINTI ABDUL MALEK",
    "DELLA QIESYA BINTI SHAHRILDELA",
    "FATIMA FARISYA BINTI RONNIE",
    "HARITH RAYYAN BIN ABDUL HADI",
    "MASYITAH BINTI MUHAMMAD SHAZWI",
    "MOHAMAD DANISH ASYTAR BIN MOHAMAD HAFIZ",
    "MUAZ RAYYAN BIN MOHAMAD SALLEH",
    "MUHAMMAD ADAM THAQIF BIN MOHD AZMI",
    "MUHAMMAD NAUFAL IMAN BIN NOOR AZIZUL",
    "MUHAMMAD ZAHIN UKAIL BIN MUSLIADY",
    "NUR AFIQAH AFIAH BINTI ZULKIFLI",
    "NUR DAYANA BATRISYA BINTI NORISAM",
    "NUR IZZATI SYAZWANI BINTI MOHD IRMAN",
    "NUR NADZIRAH SAFWAH BINTI FARID",
    "NURSYARIFA HANNA BINTI MOHD SHAFENDI",
    "NURUL FARHANA BINTI MAZLAN",
    "NURUL HUSNA BINTI AHMAD PAUZI",
    "PUTERI BALQIS BATRISYIA BINTI MUHAMAD AQBAL",
    "SHARIFAH NURDINI FARZANA BINTI SYED ASRI",
    "SITI NUR FASHARINA BINTI YAZID",
    "SUHA 'ADNIE BINTI FATHULLAH",
    "WAN FAZLIN AMIRA BINTI MIOR MUHAMAD RAZIS",
],

"2 SVM BPM": [
    "SILA PILIH",
    "AHMAD FARIS BIN AHMAD SOFIEN",
    "AIYANI BINTI SAZALI",
    "ASYRAAF DANIAL BIN MOHD HUZAIFA",
    "EHMAD SOKHIPOL ISHRAF BIN SOKHIPOL AKMAM",
    "INDAH NUR SYIFA BINTI NAHARANUAR",
    "MUHAMMAD AMSYAR IMRAN BIN MOHD TERMIDI",
    "MUHAMMAD MUAZ BIN AZLI",
    "NOOR HANNA SABRINA BINTI MOHD HANAFFIAH",
    "NUR ADRIANA BINTI MOHD ROSNI",
    "NUR AFRIN NAJWA BINTI ABDULLAH",
    "NUR AMIRAH BATRISYIA BINTI MOHD AZLAN",
    "NUR HAKIMI DANISH",
    "NUR INAS NABIHAH BINTI MOHD RIZAL",
    "NUR RAIHAN FARHANA BINTI MOHD FIRDAUS",
    "NUR SYABILA SUFFIYAH BINTI SAIFUL",
    "NUR ZAHRAA' BINTI MOHD ZAHARIZAL",
    "NURSHAHIRAH BINTI KAMARUDDIN",
    "NURUL NASUHA BINTI SOFIAN",
    "PUTERA MUHAMMAD DANIAL BIN AMY AZNAQUIDDIN",
    "PUTERA MUHAMMAD DANISH BIN AMY AZNAQUIDDIN",
    "PUTERI AISYAH NATASHA BINTI ABDUL RA'UF",
    "PUTRI NUR AINA BATRISYIA BINTI MOHD YUSRON WIRAN",
    "QAISARA BATRISYIA BINTI MOHD NURUL AZMI",
    "RABI'ATUL NABILA BINTI ZAMZUNIZAM",
    "'AIN SUFIYYAH BINTI ABDULLAH",
],

"2 SVM HSK": [
    "SILA PILIH",
    "ADRISYAM ZAMIN BIN SUMARNO",
    "AYU NABIHAH BINTI MOHD.MHASA'ARIL",
    "BALQIS AUFA BINTI MOHAMED IZUAN",
    "MIRZA IMAN HAIDAR BIN MOHAMAD ZAKI",
    "MUHAMMAD AISY AJMAL BIN MOHD NAIM",
    "MUHAMMAD DANISH IMRAN BIN SHAMSUDDIN",
    "MUHAMMAD SYAMIL MARTIN BIN ZAIDI",
    "MUHAMMAD WASIL ZHARFAN BIN NOR ZAIDI",
    "NUR ADILAH HUSNA BINTI SHAHRIZAIDI",
    "NUR AIN NAJJAH BINTI NOR JAMANI",
    "NURQAISARA UZMA BINTI MOHD SHUKOR",
    "NURSYAMIMI BATRISYIA BINTI SHAMSUL BAHARI",
    "SHAHRUL ZAQUAN BIN ZULHISHAM",
    "SOFIAH BINTI NAHAR",
    "WAFI IQBAL BIN MOHD SHAHRIL",
],

"2 SVM HBP": [
    "SILA PILIH",
    "BATRISYIA BALQIS BINTI MOHD SHAHRIL",
    "HAIFA HIDAYAH BINTI MOHAMAD SAIDI",
    "KHAIRUNNISA SOFEA BINTI AZEMI",
    "MUHAMMAD ADAM MUHAIMIN BIN MOHAMED FADZLI",
    "MUHAMMAD ADIFF BIN AZARUL AKHMAL",
    "MUHAMMAD DANIAL ADIB BIN MD FAIZAL",
    "MUHAMMAD FARISH IMTIYAZ BIN MOHD NOR HISHAMUDIN",
    "MUHAMMAD IKRAM DANISH BIN NOR EFENDI",
    "NOR RABBIHA BINTI ABD RAZAK",
    "NUR AIZATUL HUSNA BINTI HOSRI",
    "NUR ATIERAH SYAZWIEN BINTI MOHD ROSWADI",
    "NUR FAIZZATUL UMEERAH BINTI AHMAD FAUZI",
    "NUR RADHIATUN SALWA BINTI JAMALUDDIN",
    "NUR ZAKIAH HANNAN BINTI ABDUL ISHAM",
    "NURFARHANA DAMIA BINTI HANAFI",
],

"2 SVM KMK": [
    "SILA PILIH",
    "AINUR SURFINA BINTI SUHAIZARD",
    "AIRIEL HAIQAL BIN MOHD FADZIL",
    "AISYAH SAFIYYA BINTI SHAIFUL",
    "ANAS ZAQUAN BIN MOHD SUFIEZ",
    "ANIS ZAKIAH BINTI MOHD AZIZEE",
    "AQEELA NUR DARWISYAH BINTI AFDZAL HAFIZIE",
    "AZRA NURLISSA BINTI ABDULLAH SUHAIMI",
    "DANISH ISKANDAR BIN IDRUS",
    "DHIYA IMAN WADHIHAH BINTI MOHD SUHAIMI",
    "DINIE DANISH ZAKI BIN ABDUL RAZZAQ",
    "INTAN ALLESYA BINTI MOHD AZRI",
    "INTAN NORBAEYAH BINTI MOHD ZULHATTAR",
    "LISA KARMILA BINTI MOHD SALLEH",
    "MIA YASMIN BINTI ERRESAFRINAL",
    "MOHAMAD SHAHZRUL ANAS BIN MOHD SHAHRUL ANUAR",
    "MOHAMMAD ADAM HAIKAL BIN MOHD AZLI",
    "MUHAMMAD AFLIQUE WAFEEY BIN EZARUDDIN",
    "MUHAMMAD FAHMI MU'IZZ BIN ABU BAKAR",
    "MUHAMMAD HARIZ IMAN BIN ZAMHARIZAD",
    "MUHAMMAD IERFFAN BIN MOHD SHAHREN",
    "NUR ALIFAH ILYANA BINTI SHAMSUL IZWAN",
    "NUR ALISHA SAFA BINTI MOHD SHARFAN",
    "NUR DANIA ELYSHA BINTI NIK KHAIROL ANEZAM",
    "NUR HANANIA BINTI SUHAIZI",
    "NUR IMAN ALYSSA BINTI HUSAIF @ ZA'ABA",
    "NURIN ALYAA HUSNA BINTI AZIZI",
    "NURUL NUHA BINTI MOHD YAZID",
    "SUFI AZFAR MUSTAQIM BIN ANUAR",
    "WAN NUR HANEES BINTI MIOR FADZLEE",
    "YUSRINA AMNI BINTI YUKHAIRI",
],

"2 SVM KPD": [
    "SILA PILIH",
    "AHMAD AKMAL ARFAN BIN MOHD EFFENDY",
    "DAMIA MAISARA BINTI MOHD JUMARULHIZAM",
    "DANISH AKMAL BIN FAUZI",
    "ELMAN HARITH BIN MOHD NORHISHAM",
    "IRISYA JASMINE BINTI EDDY NORSHAH",
    "MOHAMAD HARITH RIFQI BIN MOHD MAUUDUDI",
    "MUHAMMAD ADIF HASYIMI BIN MOHD KHAIROL NIZAM",
    "MUHAMMAD AERIZ IEMAN BIN ZURIN",
    "MUHAMMAD AFIQ DANIAL BIN ROSLI",
    "MUHAMMAD ALIF HAIQAL BIN ZAIDE",
    "MUHAMMAD NAQIUDDIN NAZMI BIN ABDULLAH",
    "MUHAMMAD NU'MAN BIN MOHD HAZWAN",
    "NORADAWIYAH HAWA BINTI MIZWAN OTHMAN",
    "NUR DAMIA ATIQAH BINTI ANWAR SADAT",
    "NUR TASNIM AMANI BINTI MOHD SHAHROM",
    "NURUL BALQIS BINTI MOHD SUBHI",
    "SALSABEELA BINTI MOHD SAIFUL A'DLI",
    "WAN DARWISH ZAFRI BIN AHMAD EHSAN",
    "ZARA SYAHEERA BINTI ZUHAIRI",
    "MUHAMMAD THAQIF JAMSYIR BIN MOHAMED TAJRI (23.9.24)",
],

# ======================================================
# 1 SVM (SEMUA KELAS)
# ======================================================
"1 SVM BAK": [
    "SILA PILIH",
    "ADRIANA MAISARAH BINTI SHAH RIDZAL",
    "AFIQ SYAUQI BIN ASNIZAIRY",
    "MARISSA ILMI BINTI ZAIRUL",
    "MUHAMMAD ADIB NAJWAN BIN ERDY IZWAN",
    "MUHAMMAD ASYRAAF BIN MOHD SAYUTI",
    "MUHAMMAD HAQIMIE DANIEL BIN MUHAMMAD HAFFIZ",
    "MUHAMMAD RIFQI RAIHAN BIN MOHD SHAHRAIZ",
    "MUHAMMAD SYAAMIL HAKIMI BIN MOHD ZAIDE",
    "NIK DAMIEN NASHRIN BIN NIK MOHD MALEK FAIDZAL",
    "NOR ALEESYA SOFEA BINTI MOHD SHAH RILRIZAM",
    "NUR AIMY FATINA BINTI MOHD ADNAN",
    "NUR DAMIA BATRISYA BINTI FADZIL",
    "NUR DHIA ADRIANA BINTI ABDULLAH",
    "NUR IRDINA SYIFAA BINTI RUHAIZAM",
    "NUR IZZATI SYAZWANI BINTI NORAFISZAL",
    "NUR MAISARAH IZZATI BINTI NUR MUHAMMAD IQBAL",
    "NUR SHAFIQAH DARWYSHA BINTI ZUANI",
    "NUR SYAHRINA ELLYANA BINTI MOHAMAD NOR SANI",
    "PUTERI AININ SOFIYA BINTI RAZALI",
    "PUTERI ALIYAH NATASHA BINTI MOHAMAD RAZALI",
    "QAISARA HANA BINTI AZLAN",
    "SITI SAFIYYAH BINTI HALIUDIN",
    "SITI UMAIRAH BINTI HELMI",
    "SOFIA BINTI SYAFIZ",
    "TUAN NUR NADRAH BINTI TUAN DAUD RAHIMI",
],

"1 SVM BPM": [
    "SILA PILIH",
    "AHMAD RAZIQ AFIF BIN MOHD SHUKRI HANAFI",
    "ALIF ALFIAN BIN AZLI",
    "ANIS NAJIHA KHOO BINTI AHMAD JOHAN",
    "ANIS SURAYA BINTI MOHD SAFWAN",
    "AUNI FITRISHA HAZIRA BINTI MOHAMMAD ARIF",
    "ELIEZSANAJWA BINTI KAMAL",
    "INTAN NUR UMAIDAH BINTI MOHD NORHEKMAT",
    "KAISARA ALEESYA BINTI KAMARUL AZIZ",
    "KEESHA SALSABILA BINTI MOHAMAD JOHARI",
    "MARLISA ZULAIKHA BINTI JASMI",
    "MUHAMMAD ARIFF BIN RAMLI",
    "MUHAMMAD DANISH IQRAM BIN ABDULLAH",
    "MUHAMMAD HAZIQ IMAN BIN AHMAD FADHLI",
    "MUHAMMAD NAJMI HARIDZ BIN AFINDI",
    "MUHAMMAD QUSYAIRI BIN ABDUL HADI",
    "NUR AFIRATUL ABIDA BINTI ISWARDI",
    "NUR AIN BINTI MOHD YUSLAINI",
    "NUR AMMIRA ZULAIQHA BINTI MOHAMMAD IQBAR",
    "NUR DELISHA IRDINA BINTI MOHD YASMIZI",
    "NURFAIZAM FIRZANIE BINTI MOHD FAIRUZ",
    "NURNASRIN SYUHADA BINTI MOHD AZLIN",
    "NURUL AIN NADIA BINTI ABDULLAH",
    "QASEEH QASRINA BINTI ROSLAN",
    "SITI ZOONNIE AL-JUNNAH BINTI MOHAMMAD",
    "WAN NUR AYRA BINTI MOHD AZLAN",
],

"1 SVM HSK": [
    "SILA PILIH",
    "'AISYAH UMAIRAH BINTI ZUWAIRI",
    "AFIQ NAIM BIN MOHD NOR AZMAN",
    "FARISH FAHMI BIN MUHAMMAD FADELI",
    "IRDYNA UZMA BINTI MOHAMAD AZIZI",
    "IZZ HAZZIQ BIN SHAHRUL ASHAR",
    "MUHAMAD SHAFIR AIMAN BIN MOHAMAD FIRDAUS",
    "NUR ARINA FATANIAH BINTI MOHD FIZAL",
    "NUR DAMIA BATRISYIA BINTI AHMAD AZIZUDDIN",
    "NUR FATIN ALIYA BINTI HASBI",
    "NUR FATINI BINTI MOHD FARID",
    "NUR IRISYA QISMIYA BINTI ZARUL",
    "NURIN FADHILAH BINTI MOHD FAIZAL",
    "PUTERI NUR NAJEEHA BINTI ZUBIR",
    "SITI ZULAIKHA BINTI ZULKARNINE",
    "SYAH ZAFFRAN BIN SHAHREEYMAN",
    "UWAIS AMIR ALQARNI BIN KAMAR ZAKI",
],

"1 SVM HBP": [
    "SILA PILIH",
    "ADAM UQAIL BIN ABDUL HAYY",
    "ANAS HAKIM BIN MOHD HAFIDZ HADI",
    "HANI NABILA BINTI RHOMA HERWANA",
    "MIA MAISARA AFIQA BINTI MEOR AMRAN",
    "MUHAMMAD AL BARRA'Q BIN ABDUL HAFFIDZ",
    "MUHAMMAD FIRDAUS BIN MISNAN",
    "NUR ALIA AMANI BINTI ABDULLAH",
    "NUR ANIS ALLIEYNA BINTI MOHD ZAMRI",
    "NUR ARIEQA DALIELA BINTI ROZAIDI",
    "NUR FARAHIYAH ELLEYANA BINTI MOHD RIZAL FAHMI",
    "NUR REEZQI INESSA BINTI RAFAE",
    "NUR WAFA IRDINA BINTI MOHD FAIZAL",
    "NURSYAHEERA QISTYNA BINTI SUKRI",
    "NURUL QISTINA HUDA BINTI MOHD HARPIZI",
    "SYABIL ADLI BIN SAIFUL ADLI",
    "MUHAMMAD FARIZ AIMAN BIN MOHD FAUZI",
],

"1 SVM KMK": [
    "SILA PILIH",
    "ABQORIY IMTIYAAZ ZAKY BIN NUBLAN ZAKY",
    "AHMAD FADLIN ZULFAQAR BIN ABDUL FATEH KAMIL",
    "AHMAD FAIZ SYAREME BIN AHMAD SANAWI",
    "AIRISYA KARMILA DANIA BINTI MOHAMAD KHAIRI",
    "ANIS HUMAIRAH BINTI MOHD YUSSOF",
    "FARHANA KHALISA BINTI ABD HALIM",
    "FATIN AUNI IRDINA BINTI MOHD SUHAIMI",
    "JAZMINA AMANI BINTI MOHD NAJIB",
    "KHALILAH ADNINA BINTI AKUK @ ANUAR",
    "MIA SYAHMINA BINTI SHAHRIL FAHMI",
    "MUHAMMAD AMIR HARIZ BIN MOHD MAHIZAN",
    "MUHAMMAD EZZ EDDIN BIN MOHD SATAR",
    "MUHAMMAD RAYYAN BIN RAZALI",
    "NORIZZUDIN RIFQI BIN NORDIN",
    "NUR AFIQAH BINTI MOHAMAD FAIZAL",
    "NUR ALEESYA QAISARA BINTI SHAH RAZIE",
    "NUR DAMIA AFRINA ABID BINTI ABDULLAH",
    "NUR DIANAH SYAHMINA BINTI MOHD ZAIHARMI",
    "NUR PUTRI FARAH BINTI NOOR AZLAN",
    "NUR SYIFA ALEEYA BINTI NOORSHARIZAL",
    "NUR ZULAIKHA ASYIQAH BINTI ZULKIFLEE",
    "NURQAIRINA AZ ZAHRA BINTI MOHD KHAIRUL AZHAR",
    "NURUL AYESHAH DIYANAH BINTI AHMAD SHAHRUL NIZAM",
    "NURUL NASREEN RAMADHANI BINTI MUSTAQ AHMAD",
    "PUTERI SHARINA ARDINA BINTI AHMAD SHAHRIMAN",
    "RABIATUL ADAWIYAH BINTI MOHAMMAD AZHAR",
    "RYANZUL BIN BUSURAN",
    "SITI NUR SAADAH BINTI MOHD NASIR",
    "TENGKU NUR INSYIRAH BINTI TENGKU MARZUKY",
    "ZAHRAH HUMAIRA' BINTI KHAIRUL NIZAM",
],

"1 SVM KPD": [
    "SILA PILIH",
    "ADAM BIN ABDUL MALIK",
    "ADAM DARWISY BIN MOHD HAIRUL ANUAR",
    "ADAM RAHIMI BIN MD RIDZUAN",
    "AHMAD IMRAN HAKIM BIN AHMAD NIZAM",
    "AKIF ZAKWAN FATHI BIN SA'ADON",
    "ALYA BATRISYA BINTI ZULHELMY",
    "ANIS INSYERAH BINTI AZMAN",
    "ARISSA DAMIA BINTI MUHAMMAD JALIL SAYUTY",
    "ARISSA DANIA BINTI MUHAMMAD JALIL SAYUTY",
    "HASIF AISAR BIN AHMAD KAMIL",
    "MU'ADZ HAKIMI BIN SHAMSUL AZNAN",
    "MUHAMMAD FITRI BIN FAUZI",
    "MUHAMMAD AUF ZIKRI BIN SHAHRULLIZAM",
    "MUHAMMAD IZZAN HILMI BIN MOHD AZLE",
    "MUHAMMAD SYAMIL AMIL BIN MAT SOLIKHIN",
    "MUHAMMAD ZARIF NASIRUDDIN BIN ZAINUDIN",
    "NISA ZAKIRAH BINTI MOHD ZOLKAPLI",
    "NUR FARADHIA BINTI SUHAIZIHAN",
    "NUR NAZLAH ZHAFIRAH BINTI MOHD RIDZUAN",
    "PUTERI NUR QAISARA BINTI ADAM KARIM",
],

# ======================================================
# OPP
# ======================================================
"4 OPP": [
    "SILA PILIH",
    "AHMED DANIEL BIN AZHAR",
    "AIMAN SAFARAZ BIN MOHD ISMAIL",
    "AMIR HAMZAH BIN ABU BAKAR",
    "MUHAMMAD SYAHIR SUFI BIN MOHD AFFANDI",
    "MUHAMMAD SYAZWAN BIN SAMSUL IZWAN",
    "MUHAMMAD YUSUF ALQARDHAWI BIN MOHD HISAM",
    "NURUL AFIQAH BINTI AZMAN",
    "NURUL AWATIF SYAZWANI BINTI MOHD FAISAL",
    "RABIAH BALQIS BINTI MOHD KHALIS",
    "SITI NUR FARAH ASYIQIN BINTI MOHD AMINUDIN",
],

"5 OPP": [
    "SILA PILIH",
    "AHMAD MUIZZUDDIN BIN AHMAD NIZAM",
    "MIERZA MAISARAH BINTI MOHD SUHAIMI",
    "MUHAMMAD ADAM FARIZ BIN MOHD TARMIZEE",
    "MUHAMMAD DANISH AFIF BIN MOHD JENLE",
    "MUHAMMAD GIHAN BIN ZAIHAN",
    "MUHAMMAD MU'ADZ BIN AB HADI",
    "MUHAMMAD RAYYAN NABEEL BIN MOHD RISHAH",
    "NOR ASHRAF MUQRI BIN NORAZAM",
    "SYAZRIL ANIQ BIN IMAM KOIRI",
],
}

# ======================================================
# UTILITI FAIL
# ======================================================
def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def csv_path(kelas):
    return os.path.join(DATA_DIR, f"{kelas.replace(' ', '_')}.csv")

def meta_path(kelas):
    return os.path.join(DATA_DIR, f"{kelas.replace(' ', '_')}_meta.json")

def load_data(kelas):
    ensure_dir()

    # Jika file wujud → baca
    if os.path.exists(csv_path(kelas)):
        df = pd.read_csv(csv_path(kelas))
    else:
        df = pd.DataFrame(columns=CSV_COLUMNS)
        df.to_csv(csv_path(kelas), index=False)

    # Pastikan semua column baru wujud
    df = df.reindex(columns=CSV_COLUMNS)
    df["Kaedah"] = df["Kaedah"].fillna("").astype(str)

    for col in ["Tarikh 1", "Tarikh 2", "Tarikh 3"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("")

        if col not in df.columns:
            df[col] = ""

    # Fill kosong untuk numeric sahaja
    for col in ["Bayaran 1", "Bayaran 2", "Bayaran 3", "Jumlah"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df.sort_values(by="Nama", key=lambda x: x.str.upper()).reset_index(drop=True)

    return df

def save_data(kelas, df):
    df = df.sort_values(by="Nama", key=lambda x: x.str.upper()).reset_index(drop=True)
    df.to_csv(csv_path(kelas), index=False)

def load_meta(kelas):
    if os.path.exists(meta_path(kelas)):
        with open(meta_path(kelas)) as f:
            return json.load(f)
    return {}

def save_meta(kelas, data):
    with open(meta_path(kelas), "w") as f:
        json.dump(data, f)

# ======================================================
# TAJUK TAHUN
# ======================================================
def get_tahun_tajuk(kelas):
    if kelas.startswith("2 DVM"):
        return "TAHUN 4"
    if kelas.startswith("1 DVM"):
        return "TAHUN 3"
    if kelas.startswith("2 SVM") or kelas.startswith("5 OPP"):
        return "TAHUN 2"
    if kelas.startswith("1 SVM") or kelas.startswith("4 OPP"):
        return "TAHUN 1"
    return ""

# ======================================================
# PDF (HANYA KECILKAN JADUAL)
# ======================================================
def generate_pdf(kelas, df, jumlah_aktual, penasihat):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "title",
        fontSize=15,
        alignment=1,
        fontName="Helvetica-Bold",
        spaceAfter=6
    )

    subtitle = ParagraphStyle(
        "subtitle",
        fontSize=9,
        alignment=1,
        spaceAfter=4
    )

    header = ParagraphStyle(
        "header",
        fontSize=8,                 # 🔽 lebih kecil
        alignment=1,
        fontName="Helvetica-Bold",
        textColor=colors.white
    )

    cell = ParagraphStyle(
        "cell",
        fontSize=7,                 # 🔽 lebih kecil
        leading=8
    )

    elements = []
    elements.append(Paragraph(
        f"SENARAI NAMA PELAJAR {get_tahun_tajuk(kelas)} 2025",
        title
    ))
    elements.append(Paragraph(kelas, subtitle))

    if penasihat:
        elements.append(
            Paragraph(f"Penasihat Kelas : {penasihat}", subtitle)
        )

    elements.append(Spacer(1, 6))

    table_data = [[
        Paragraph("BIL", header),
        Paragraph("NAMA", header),
        Paragraph("BAYARAN 1<br/>(RM)", header),
        Paragraph("BAYARAN 2<br/>(RM)", header),
        Paragraph("BAYARAN 3<br/>(RM)", header),
        Paragraph("JUMLAH<br/>(RM)", header),
        Paragraph("JUMLAH AKTUAL<br/>(RM)", header),
        Paragraph("BAKI<br/>(RM)", header),
        Paragraph("KAEDAH PEMBAYARAN", header),
    ]]

    for i, r in df.iterrows():
        baki = jumlah_aktual - r["Jumlah"]

        # --- FIX TARIKH KOSONG (BUANG nan) ---
        t1 = "" if pd.isna(r["Tarikh 1"]) or r["Tarikh 1"] == "" else r["Tarikh 1"]
        t2 = "" if pd.isna(r["Tarikh 2"]) or r["Tarikh 2"] == "" else r["Tarikh 2"]
        t3 = "" if pd.isna(r["Tarikh 3"]) or r["Tarikh 3"] == "" else r["Tarikh 3"]

        table_data.append([
            Paragraph(str(i + 1), cell),
            Paragraph(r["Nama"], cell),

            Paragraph(f"{r['Bayaran 1']:,.2f}<br/><font size=6>{t1}</font>", cell),
            Paragraph(f"{r['Bayaran 2']:,.2f}<br/><font size=6>{t2}</font>", cell),
            Paragraph(f"{r['Bayaran 3']:,.2f}<br/><font size=6>{t3}</font>", cell),

            Paragraph(f"{r['Jumlah']:,.2f}", cell),                 # JUMLAH
            Paragraph(f"{jumlah_aktual:,.2f}", cell),               # JUMLAH AKTUAL
            Paragraph(f"{(jumlah_aktual - r['Jumlah']):,.2f}", cell),  # BAKI (BETUL)
            Paragraph(str(r["Kaedah"]) if pd.notna(r["Kaedah"]) else "", cell),  # KAEDAH
        ])

    jumlah_kutipan = df["Jumlah"].sum()
    jumlah_aktual_total = jumlah_aktual * len(df)
    baki_total = jumlah_aktual_total - jumlah_kutipan
    peratus = (df["Jumlah"] >= jumlah_aktual).sum() / len(df) * 100 if len(df) else 0

    table_data.append([
        "",
        Paragraph("<b>JUMLAH</b>", cell),
        "",
        "",
        "",
        Paragraph(f"<b>{jumlah_kutipan:,.2f}</b>", cell),
        Paragraph(f"<b>{jumlah_aktual_total:,.2f}</b>", cell),
        Paragraph(f"<b>{baki_total:,.2f}</b>", cell),
        Paragraph(f"<b>{peratus:.2f}% pelajar telah membayar</b>", cell),
    ])

    table = Table(
        table_data,
        colWidths=[28, 180, 60, 60, 60, 75, 85, 65, 120],  # 🔽 dikecilkan
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("SPAN", (1, -1), (4, -1)),
    ]))

    elements.append(table)
    doc.build(elements)
    return buffer.getvalue()

# ======================================================
# MAIN (KEKAL)
# ======================================================
def render():
    st.markdown("## SENARAI NAMA PELAJAR")

    tahun = st.selectbox("Pilih Tahun", TAHUN_OPTIONS)
    kelas_list = KELAS_OPP if tahun == "OPP" else [f"{tahun} {k}" for k in KELAS_BIASA]
    kelas = st.selectbox("Pilih Kelas", kelas_list)

    meta = load_meta(kelas)

    kohort = st.selectbox(
        "Kohort (Tahun)",
        KOHORT_OPTIONS,
        index=KOHORT_OPTIONS.index(meta.get("kohort", KOHORT_OPTIONS[0]))
    )

    penasihat = st.text_input("Penasihat Kelas", value=meta.get("penasihat_kelas", ""))
    jumlah_aktual = st.number_input(
        "Jumlah Aktual (RM)",
        value=float(meta.get("jumlah_aktual", 0.0)),
        step=1.0
    )

    if st.button("Simpan Maklumat Kelas"):
        meta["kohort"] = kohort
        meta["penasihat_kelas"] = penasihat.upper()
        meta["jumlah_aktual"] = jumlah_aktual
        save_meta(kelas, meta)
        st.success("Maklumat kelas disimpan.")

    st.divider()

    df = load_data(kelas)

    if meta.get("kohort") != kohort:
        st.info("Tiada rekod pelajar untuk kohort ini.")
        return

    edit_index = st.session_state.get("edit_index")
    nama_d, b1_d, b2_d, b3_d, kaedah_d = "", 0.0, 0.0, 0.0, "SILA PILIH"

    if edit_index is not None and edit_index < len(df):
        row = df.loc[edit_index]

        nama_d = row["Nama"]
        b1_d = row["Bayaran 1"]
        b2_d = row["Bayaran 2"]
        b3_d = row["Bayaran 3"]
        kaedah_d = row["Kaedah"]

    with st.form("form_pelajar"):
        senarai_nama = NAMA_PELAJAR_KELAS.get(kelas, [])

        if senarai_nama:
            nama = st.selectbox(
                "Nama Pelajar",
                senarai_nama,
                index=senarai_nama.index(nama_d) if nama_d in senarai_nama else 0
            )
        else:
            nama = ""

        c1, c2, c3 = st.columns(3)

        b1 = c1.number_input("Bayaran 1 (RM)", value=float(b1_d))
        t1 = c1.date_input("Tarikh Bayaran 1", value=None, key="t1")

        b2 = c2.number_input("Bayaran 2 (RM)", value=float(b2_d))
        t2 = c2.date_input("Tarikh Bayaran 2", value=None, key="t2")

        b3 = c3.number_input("Bayaran 3 (RM)", value=float(b3_d))
        t3 = c3.date_input("Tarikh Bayaran 3", value=None, key="t3")

        kaedah = st.selectbox(
            "Kaedah Pembayaran",
            KAEDAH_OPTIONS,
            index=KAEDAH_OPTIONS.index(kaedah_d)
        )

        if st.form_submit_button("SIMPAN"):
            if not nama or nama == "SILA PILIH":
                st.error("Sila pilih nama pelajar.")
                st.stop()

            jumlah = b1 + b2 + b3

            t1_val = t1.strftime("%Y-%m-%d") if t1 else ""
            t2_val = t2.strftime("%Y-%m-%d") if t2 else ""
            t3_val = t3.strftime("%Y-%m-%d") if t3 else ""

            if edit_index is not None:
                df.loc[edit_index] = [
                    nama.upper(),
                    b1, t1_val,
                    b2, t2_val,
                    b3, t3_val,
                    jumlah,
                    kaedah if kaedah != "SILA PILIH" else ""
                ]
                
                st.session_state.edit_index = None
            else:
                df.loc[len(df)] = [
                    nama.upper(),
                    b1, t1_val,
                    b2, t2_val,
                    b3, t3_val,
                    jumlah,
                    kaedah if kaedah != "SILA PILIH" else ""
                ]

            save_data(kelas, df)
            st.rerun()

    if df.empty:
        st.info("Tiada rekod pelajar.")
        return

    # ===== FORMAT RM FUNCTION (LETak ATAS SEKALI sebelum guna) =====
    def rm(x):
        try:
            return f"RM {float(x):,.2f}"
        except:
            return ""

    # ===== PREPARE DATA VIEW =====
    df_view = df.copy()

    df_view["Jumlah Aktual"] = jumlah_aktual

    if "jumlah_khas" in meta:
        for idx, val in meta["jumlah_khas"].items():
            idx = int(idx)
            if idx < len(df_view):
                df_view.loc[idx, "Jumlah Aktual"] = val

    df_view["Baki"] = df_view["Jumlah Aktual"] - df_view["Jumlah"]

    # JANGAN FORMAT RM — BIAR NUMERIC
    df_view["Bayaran 1"] = pd.to_numeric(df_view["Bayaran 1"], errors="coerce").fillna(0)
    df_view["Bayaran 2"] = pd.to_numeric(df_view["Bayaran 2"], errors="coerce").fillna(0)
    df_view["Bayaran 3"] = pd.to_numeric(df_view["Bayaran 3"], errors="coerce").fillna(0)
    df_view["Jumlah"] = pd.to_numeric(df_view["Jumlah"], errors="coerce").fillna(0)
    df_view["Jumlah Aktual"] = pd.to_numeric(df_view["Jumlah Aktual"], errors="coerce").fillna(0)
    df_view["Baki"] = pd.to_numeric(df_view["Baki"], errors="coerce").fillna(0)

    # ===== CHECKBOX =====
    df_view.insert(0, "Pilih", False)

    edited = st.data_editor(
        df_view,
        hide_index=True,
        use_container_width=False,   # <-- BAGI LEBAR IKUT SKRIN
        column_config={
            "Bayaran 1": st.column_config.NumberColumn(format="RM %.2f", width="small"),
            "Bayaran 2": st.column_config.NumberColumn(format="RM %.2f", width="small"),
            "Bayaran 3": st.column_config.NumberColumn(format="RM %.2f", width="small"),
            "Tarikh 1": st.column_config.TextColumn(width="small"),
            "Tarikh 2": st.column_config.TextColumn(width="small"),
            "Tarikh 3": st.column_config.TextColumn(width="small"),
            "Jumlah": st.column_config.NumberColumn(format="RM %.2f", width="small"),
            "Jumlah Aktual": st.column_config.NumberColumn(format="RM %.2f", width="small"),
            "Baki": st.column_config.NumberColumn(format="RM %.2f", width="small"),
        },
        disabled=[c for c in df_view.columns if c != "Pilih"]
    )

    pilih = edited[edited["Pilih"]]

    if len(pilih) == 1:
        c1, c2, c3 = st.columns(3)
        if c1.button("EDIT"):
            st.session_state.edit_index = pilih.index[0]
            st.rerun()
        if c2.button("PADAM"):
            st.session_state.confirm_delete = pilih.index[0]
        if c3.button("MEMPUNYAI ADIK BERADIK"):
            st.session_state.adik_index = pilih.index[0]
            
    if "adik_index" in st.session_state:
        st.warning("Tetapkan jumlah khas untuk pelajar ini")

        jumlah_khas = st.number_input(
            "Jumlah Aktual Pelajar Ini Sahaja (RM)",
            min_value=0.0,
            step=1.0,
            key="jumlah_khas_input"
        )

        c1, c2 = st.columns(2)

        if c1.button("SIMPAN JUMLAH KHAS"):
            df.loc[st.session_state.adik_index, "Jumlah"] = min(
                df.loc[st.session_state.adik_index, "Jumlah"],
                jumlah_khas
            )

            # Simpan dalam meta khas
            meta.setdefault("jumlah_khas", {})
            meta["jumlah_khas"][str(st.session_state.adik_index)] = jumlah_khas
            save_meta(kelas, meta)

            del st.session_state.adik_index
            st.success("Jumlah khas disimpan.")
            st.rerun()

        if c2.button("BATAL"):
            del st.session_state.adik_index
            st.rerun()
            
    if "confirm_delete" in st.session_state:
        st.warning("Anda pasti mahu padam rekod ini?")
        y, n = st.columns(2)
        if y.button("YA, PADAM"):
            df = df.drop(st.session_state.confirm_delete).reset_index(drop=True)
            save_data(kelas, df)
            del st.session_state.confirm_delete
            st.rerun()
        if n.button("BATAL"):
            del st.session_state.confirm_delete

    baki = jumlah_aktual - df["Jumlah"]
    peratus = (baki <= 0).sum() / len(df) * 100

    st.markdown(
        f"""
        <div style="
            margin-top: 20px;
            font-size: 20px;
            font-weight: bold;
            line-height: 1.6;
        ">
            Jumlah Kutipan: RM {df['Jumlah'].sum():,.2f}<br>
            Jumlah Aktual: RM {jumlah_aktual * len(df):,.2f}<br>
            Jumlah Baki: RM {baki.sum():,.2f}<br>
            Peratus Pelajar Bayar: {peratus:.2f}%
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("MENCETAK"):
        pdf = generate_pdf(kelas, df, jumlah_aktual, penasihat)
        b64 = base64.b64encode(pdf).decode()
        components.html(f"""
        <script>
        var a=document.createElement("a");
        a.href="data:application/pdf;base64,{b64}";
        a.download="senarai_nama_{kelas.replace(' ','_')}.pdf";
        a.click();
        </script>
        """, height=0)