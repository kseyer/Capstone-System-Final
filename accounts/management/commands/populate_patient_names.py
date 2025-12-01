from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate patient data from image names distributed across 2020-2025'

    def handle(self, *args, **kwargs):
        # Patient names from the images you sent
        patient_names = [
            # Image 1
            ("ABDULA", "MARIA ELENA", "F"),
            ("ABETO", "ANGELO JESSEN", "M"),
            ("ABETO", "JENEVIEVE", "F"),
            ("ABINA", "JEZRELL BELIA", "F"),
            ("ABONALES", "JO-ANN", "F"),
            ("ABONIL", "ANGEL FAITH", "F"),
            ("ABOSO", "EDEN", "F"),
            ("ABOSO", "EMILY P", "F"),
            ("ABOSO", "HANS FRANCIS", "M"),
            ("ACUYADO", "PRINZZLE", "F"),
            ("ALAPO", "JINLEI", "M"),
            ("ALBA", "SURFFY MAE", "F"),
            ("ALEJORA", "NOEMI", "F"),
            ("ALIGARVES", "RHODORA", "F"),
            ("ALIGUI", "DOLORES BUSTAMANTE", "F"),
            ("ALINIO", "JOELYN", "F"),
            ("ALISEN", "CHRISTINE", "F"),
            ("ALOTENCIO", "GERMILYN", "F"),
            ("ALOTENCIO", "NOLI", "F"),
            ("ALVARADO", "JOSELITO", "M"),
            ("ALVAREZ", "JASMIN GRACE", "F"),
            ("AMARA", "ARLENE", "F"),
            ("ANDRADA", "KHRYSTELLE R", "F"),
            ("ANILADO", "RODINA C", "F"),
            ("ANTONIO", "MAUREEN BARAOG", "F"),
            ("AQUILLA", "ANGELINA", "F"),
            ("ARAULLO", "KISINER", "F"),
            ("ARDEVELA", "LOVE", "F"),
            ("ARIMBOS", "NORMA A", "F"),
            ("ARQUINTILLO", "SHENNIA", "F"),
            ("ARRIENDA", "JOCELYN", "F"),
            ("ARTIEDA", "GERARDO", "M"),
            ("ASTRE", "SAMANTHA", "F"),
            ("ATILON", "NATASHA", "F"),
            ("ATINGRO", "ROSE JANE", "F"),
            ("AURELIO", "ANA KATRINA B", "F"),
            ("BAHAGUE", "ARSEL JANE", "F"),
            ("BALANGAO", "CARMENCITA", "F"),
            
            # Image 2
            ("BALAZUELA", "EVANGELINE A", "F"),
            ("BALOLOT", "JULIENNE", "F"),
            ("BALSICAS", "LILIBETH", "F"),
            ("BALTAZAR", "MARIBEL", "F"),
            ("BALTAZAR", "WELSITA", "F"),
            ("BANASIG", "DESIREE BANILLA", "F"),
            ("BANASIG", "PASCUALITO", "M"),
            ("DANIEL", "AIDA FE GONZALES", "F"),
            ("BANIEL", "ANDREI", "M"),
            ("BANIEL", "CHERYL ANNE GONZALES", "F"),
            ("BANOT", "APRIL ROSE", "F"),
            ("BANTIGUE", "CHAT", "F"),
            ("BANTIGUE", "MARIANNE", "F"),
            ("BANTIGUE", "MARY ANN", "F"),
            ("BARBO", "ANA", "F"),
            ("BARBO", "GEMAA", "F"),
            ("BARBOSA", "ANN MAGDALENE", "F"),
            ("BARBOSA", "TERRENCE", "M"),
            ("BARDOQUIN", "KYLA JANE", "F"),
            ("BARILLO III", "BENEDICTO", "M"),
            ("BARNIZO", "CHARLES", "M"),
            ("BARON", "STEFANY", "F"),
            ("BAYER", "ANDREI", "M"),
            ("BAYER", "MA. THERESA", "F"),
            ("BAYON-ON", "NELIA", "F"),
            ("BELECTINA", "JOSHUA", "M"),
            ("BELECTINA JR", "RONNEL", "M"),
            ("BENDOL", "JON LEXUS", "M"),
            ("BENDOL", "JUNE ANNE", "F"),
            ("BENIABON", "RENZIE SALBINO", "M"),
            ("BENIABON", "RYAN", "M"),
            ("BENIGNOS", "LEONARDO", "M"),
            ("BENJAMIN", "ALVIRA", "F"),
            ("BERANIO", "LAILAH", "F"),
            ("BERATIO", "RAQUEL", "F"),
            ("BERAYO", "GENELLE MONDRAGON", "F"),
            ("BERJIT", "APRIL ROSE", "F"),
            ("BERJIT", "JOHN EARL", "M"),
            
            # Image 3
            ("CARMONA", "KYLA", "F"),
            ("CARMONA", "MARY KATE BONCALON", "F"),
            ("CARMONA", "ROMELA BONCALON", "F"),
            ("CASIDO", "CARMI JOY", "F"),
            ("CASTILLER", "JOHANAN", "M"),
            ("CASTILLO", "DREIFUZ TEOVIC", "M"),
            ("CASTILLO", "JOCILYN", "F"),
            ("CASTILLO", "MARIE JHUN MONDEJAR", "F"),
            ("CASTOR", "KEVIN", "M"),
            ("CASTOR", "MIKHAELA", "F"),
            ("CASTRO", "FERNAND", "M"),
            ("CASTRO", "IRMA", "F"),
            ("CASTRO", "IVAN AUSTINE", "M"),
            ("CASTRO", "KEVIN WILLIAM", "M"),
            ("CATAPANG", "JOY", "F"),
            ("CELIS", "GENETTE", "F"),
            ("CELIS", "LEDA", "F"),
            ("CENTERING", "MA CHRISTINA", "F"),
            ("CHAUCA", "MALOU DELA CRUZ", "F"),
            ("CHAVEZ", "ROSALIE", "F"),
            ("CLAVERIA", "MIKE", "M"),
            ("CLAVERIA", "VIRGINIA F", "F"),
            ("CLAVERIA", "WILSON", "M"),
            ("CLELO", "CATHERINE", "F"),
            ("CONDING", "RENEE", "F"),
            ("CONSTANTINO", "SHAIRA", "F"),
            ("CONTE", "GLENDA", "F"),
            ("CONTE", "JUN REY", "M"),
            ("CONTRERAS", "LORENZO", "M"),
            ("CORRAL", "EDA", "F"),
            ("COSAS", "RAINER CAMBRONERO", "M"),
            ("COSCOS", "RAYVEN CAMBRONERO", "M"),
            ("COSCOLLUELA", "MIGUEL", "M"),
            ("COSCOLLUELA", "TERESA", "F"),
            ("CRISTALES", "MIKE", "M"),
            ("CRUZ", "RITZ", "M"),
            ("CRUZ", "VANCE", "M"),
            ("CURAMMENG", "JENNELYN", "F"),
            
            # Image 4
            ("DELA PENA", "NEMIA F", "F"),
            ("DELA TORRE", "MARIA SABRINA", "F"),
            ("DELA TORRE", "MARIA SAMANTHA", "F"),
            ("DELA TORRE", "NATHANIEL", "M"),
            ("DELA TORRE", "ROLINA", "F"),
            ("DELGADO", "ANTON JOHN", "M"),
            ("DELGADO", "ANGELIE FRANZ", "F"),
            ("DELGADO", "ANTON", "M"),
            ("DELGADO", "CARLOS", "M"),
            ("DELGADO", "EDNA ELAINE", "F"),
            ("DELGADO", "JUANA", "F"),
            ("DELGADO", "MAY", "F"),
            ("DELGADO", "MELINDA", "F"),
            ("DELGADO", "MICHAEL ANGELO", "M"),
            ("DELGADO", "SUSAN", "F"),
            ("DESPUIG", "JESSA P", "F"),
            ("DEVELA", "ELIZABETH", "F"),
            ("DEVELOS", "LEANN LORRAINE RAMOS", "F"),
            ("DEWALA", "CHRISTINE", "F"),
            ("DIESTO", "TYRA L", "F"),
            ("DIEUMANO", "EVELYN", "F"),
            ("DILE", "BONA", "F"),
            ("DILE", "NYK", "M"),
            ("DILE", "ROWENA", "F"),
            ("DILE", "RYK", "M"),
            ("DIROPON", "ATTY ERNESTO", "M"),
            ("DIO", "EILEN", "F"),
            ("DIOMAS", "DENMART", "M"),
            ("DIVINGACIA", "ANGELA", "F"),
            ("DIZON", "JEN MAY", "F"),
            ("DIZON", "JERUEL IAN", "M"),
            ("DIZON", "RIZZA", "F"),
            ("DONARIA", "NIÑALIZA", "F"),
            ("DONARIA", "JOAN", "F"),
            ("DONARIA", "JOJI", "F"),
            ("DONASCO", "ABIGAIL", "F"),
            ("DONASCO", "AMABELLE VICTORIA", "F"),
            
            # Image 5
            ("EINOSAS", "JV SNOOK", "M"),
            ("EINOSAS", "KAT", "F"),
            ("EJERCITO", "EDERLYN GONZAGA", "F"),
            ("EJERCITO", "RITZ", "M"),
            ("ELLAB", "MARY ROSE", "F"),
            ("EMBAJADOR", "MICHAEL", "M"),
            ("EMBANG", "ERIKA", "F"),
            ("ENGRACIA", "LOLITA", "F"),
            ("ENTAPAN", "JENELYN", "F"),
            ("EPLAGO", "MA. CRISTINA JACOLBE", "F"),
            ("ESPERANZA", "JELLY MAE", "F"),
            ("ESPELETA", "PAUL SEMBRANO", "M"),
            ("ESPIRITU", "MAAN", "F"),
            ("ESTRADA", "REIN", "F"),
            ("EUGENIO", "RONEL ERECE", "M"),
            ("EVANGELISTA", "GLANE", "F"),
            ("FAMOSO", "KATRINA SHEENA", "F"),
            ("FARENELY", "CORNELIO HOPE LEGASPINA", "F"),
            ("FERNANDEZ", "CHARLIE", "M"),
            ("FERRER", "WILLIE JANE", "F"),
            ("FIRMAN", "MA. ANNA FATIMA PALPARAN", "F"),
            ("FOJADO", "ALYN", "F"),
            ("FUENTES", "KIM", "F"),
            ("GABALLO", "KRISTA AINEE", "F"),
            ("GALLEGO", "MRS DIANE", "F"),
            ("GALLO", "ANDREA BIELLE", "F"),
            ("GALLO", "SHARON", "F"),
            ("GALLO", "JOHAN NINO M", "M"),
            ("GALLO", "JOHANNES NINO", "M"),
            ("GAMBOA", "KIM PIAMONTE", "F"),
            ("GARLAD", "MOMINA", "F"),
            ("GANZA", "GLENN", "M"),
            ("GANZA", "MYLENE", "F"),
            ("GARGALLANO", "JERYMAY", "F"),
            ("GARTOSE", "KATELYN", "F"),
            ("GARZON", "CHRISTIAN", "M"),
            ("GRAZON", "NEPH", "M"),
            ("GASTON", "SHAIRA REYES", "F"),
        ]

        years = [2020, 2021, 2022, 2023, 2024, 2025]
        occupations = [
            "Teacher", "Student", "Nurse", "Engineer", "Accountant", 
            "Business Owner", "Call Center Agent", "Designer", "Driver",
            "Housewife", "Office Worker", "Sales Clerk", "Manager",
            "Social Worker", "Government Employee", "BPO Employee",
            "Architect", "Police Officer", "Seaman", "OFW", "Retired",
            "Civil Engineer", "Lawyer", "Judge", "Virtual Assistant",
            "Private Company", "School Nurse", "Reporter", "Secretary",
            "CSR", "Operation Manager", "Caregiver", "Junior Architect",
            "Accounting Clerk", "Admin Supervisor", "ADAS J",
            "ESL Teacher", "Research Nurse", "Govt Lawyer"
        ]

        addresses = [
            "Bacolod City", "ERORECO", "Taguiling, Bacolod City", 
            "EB Magalona", "Rosario Heights Subd. Bacolod City",
            "Villamonte", "Silay City", "Banago, Bacolod City",
            "Capitol Ville", "Villa Angela Subd. Bacolod City",
            "Canetown Subdivision, Victorias City", "Antique",
            "Elena Subd. Silay City", "Brgy. Lantad, Silay City",
            "Pasay City", "Buenretiro, Talisay City", "Bata Subd. Bacolod City",
            "Mandalagan", "BRGY. CABUG, B. C", "BUKIDNON ST PILI BACOLOD CITY",
            "Silay City", "ALTIS", "BUENA ROYALE BACOLOD CITY",
            "BRGY. GRANADA, BACOLOD CITY", "Nananala", "Brgy Bata",
            "Victorias City", "BRGY PUNTA TAYTAY", "DUMAGUETE",
            "BACOLOD CITY", "CALONG CALONG AIRPORT BACOLOD CITY",
            "ALTIS", "PUENTEBELLA SUBD. BACOLOD CITY", 
            "D5 L8 VILLA RAMOS BRGY. VILLAMONTE BACOLOD CITY",
            "GOLDEN RIVER, TACULING", "FORTUNE TOWNE BACOLOD CITY",
            "AIRPORT SUBD", "BATA SUBD. BACOLOD CITY", "IRELAND",
            "CARMELA SUBD. TALISAY CITY", "TALISAY CITY",
            "BRGY MAMBULAC, SILAY CITY", "BRGY. GRANADA, BACOLOD CITY",
            "LIBRA ST. JR. TORRES SUBD BACOLOD CITY", "Silay City",
            "BRGY. SINGCANG AIRPORT, BACOLOD CITY", "CEBU CITY",
            "BRGY. VILLAMONTE BACOLOD CITY", "CALONG CALONG AIRPORT BACOLOD CITY",
            "BRGY CABUG, TALISAY CITY", "Brgy BUBOG TALISAY CITY",
            "BRGY BATA", "MANSILIGAN, BACOLOD CITY", "BRGY. BATA, BACOLOD CITY",
            "LACSON ST, BACOLOD CITY", "BINALBAGAN", "VILLA ANGELA",
            "MANSILBANGAN", "brgy guinhalaran, silay city", "USA", 
            "Tangub, Bacolod City", "ERORECO SUBDIVISION BACOLOD CITY",
            "PLANTAZIONE VERDANA, TALISAY CITY", "CAMELLA HOMES",
            "CAMELLA MANDALAGAN", "CAMELLA", "AIRPORT SUBD", 
            "ACABUG, BACOLOD CITY", "EAST HOMES 2", "EAST HOMES 2 BACOLOD CITY",
            "COPENHAGEN, DENMARK", "INAYAWAN CALIVO", "MANVILLE ROYALE, B. C",
            "ANTIPOLO CITY", "BRGY PUNTA TAYTAY", "BRGY. BUBOG, TALISAY CITY"
        ]

        created_count = 0
        skipped_count = 0

        self.stdout.write(self.style.SUCCESS('Starting patient population...'))

        for last_name, first_name, gender in patient_names:
            # Generate username from first and last name
            username_base = (first_name.split()[0] + last_name.split()[0]).lower().replace(" ", "")
            username_base = ''.join(e for e in username_base if e.isalnum())[:12]
            username = username_base
            
            # Check if username exists, if so add number
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1
                if counter > 100:
                    self.stdout.write(self.style.WARNING(f'Skipping {first_name} {last_name} - too many duplicates'))
                    skipped_count += 1
                    break
            
            if counter > 100:
                continue

            # Random year for registration
            year = random.choice(years)
            
            # Generate random date within the year
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
            days_between = (end_date - start_date).days
            random_days = random.randint(0, days_between)
            date_joined = start_date + timedelta(days=random_days)

            # Generate phone number
            phone = f"09{random.randint(100000000, 999999999)}"

            # Random occupation and address
            occupation = random.choice(occupations)
            address = random.choice(addresses)

            # Civil status
            civil_status = random.choice(['single', 'married', 'widowed', 'divorced', 'separated'])

            # Gender
            gender_value = 'male' if gender == 'M' else 'female'

            # Create or skip if exists
            if not User.objects.filter(username=username).exists():
                try:
                    user = User.objects.create_user(
                        username=username,
                        first_name=first_name.title(),
                        last_name=last_name.title(),
                        email=f"{username}@example.com",
                        password="password123",
                        user_type='patient',
                        phone=phone,
                        address=address,
                        gender=gender_value,
                        civil_status=civil_status,
                        occupation=occupation,
                        date_joined=timezone.make_aware(date_joined),
                        created_at=timezone.make_aware(date_joined),
                    )
                    created_count += 1
                    
                    if created_count % 10 == 0:
                        self.stdout.write(self.style.SUCCESS(f'Created {created_count} patients...'))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating {first_name} {last_name}: {str(e)}'))
                    skipped_count += 1
            else:
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {created_count} patients'))
        self.stdout.write(self.style.WARNING(f'⚠️  Skipped {skipped_count} patients (already exist or errors)'))
        self.stdout.write(self.style.SUCCESS('\nPatient distribution by year:'))
        
        for year in years:
            year_start = datetime(year, 1, 1)
            year_end = datetime(year, 12, 31)
            count = User.objects.filter(
                user_type='patient',
                date_joined__gte=timezone.make_aware(year_start),
                date_joined__lte=timezone.make_aware(year_end)
            ).count()
            self.stdout.write(self.style.SUCCESS(f'  {year}: {count} patients'))
