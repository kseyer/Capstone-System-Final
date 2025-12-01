from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate patient data from image names distributed across 2020-2025'

    def handle(self, *args, **kwargs):
        # All patient names from the images - 500+ patients
        patient_names_data = """
LUPO, JAMELLA|F
LUPO, JOAN|F
LUPO, JUNELL|F
MACABERO, PATRICIA|F
MACASA, HERDION|M
MACARAEG, REGINE D|F
MAGALONA, APRIL|F
MAGBANUA, ALDER|M
MAGBANUA, NONA|F
MAGBANUA, NORICAH LEIGH|F
MAGBANUA, SHERRY|F
MALACAMAN, CRISMARIE|F
MALACAMAN, IRIEL MAY|F
MALINAO, RUBY M|F
MALINAO, MA. ISABEL MANAOG|F
MALINAO, ROLAND MOISES|M
MAMALIAS, DAVE|M
MAMALIAS, AICE|F
MANALO, LAWRENCE|M
MANALO, MARY KATHERINE|F
MANIACOP, MA LINA|F
MAQUIRAN, MA. GERTRUDE|F
MARAVILLA, TESS|F
MARQUEZ, DYAN TURONGBANUA|F
MARTUS, JAMREY|M
MATHONG, FRITZIE|F
MAULLON, ROMMEL III|M
MEDIANERO, NINA|F
MELOCOTON, RAMON|M
MINASE, DESIREE ROSE AMADOR|F
MINASE, NADINE RUTH|F
MISSION, ROSELLE GERALDOY|F
MIURA, RYLEA|F
MOLINA, ROSALIE|F
MOMBLAN, APRIL ROSE|F
MOMONGAN, CLAIRE ANN|F
MONCADA, QUEENY|F
MONGE, MARICAR GARIN|F
GUSTILO, CHRISTINE|F
GUSTILO, JILLIAN D|F
GUSTILO, JOJIE CUAPOS|M
GUSTILO, MARIA ROSIELYN|F
GUSTILO, NAYAN GAYLE|F
HILADO, JHANICE|F
HINLO, ALIA|F
HORTINELA, KRIZZA JANE|F
HOWARD, KATE|F
ILANGOS, QUEENIE MARYH|F
ILANO, ANGELA|F
ILANO, ANGELO|M
ILANO, EVA ROSE|F
ILANO, JILIAN|M
ILANO, JIMMY|M
ILEAN, RJ|M
INOCENCIO, MARY ANN|F
IRORITA, GENEBETH|F
ISIDTO, ARABELLA GRACE|F
ISIDTO, EMMANI JANELLE|F
JACOLBE, ELSA EVANGELISTA|F
JAEN, CHA ANN ROSALES|F
JAMELO, EFRAIM|M
JAMELO, PAMELA|F
JERMIA, YOLANDA|F
JIMENEA, MATTHEW|M
JISON, AILEEN|F
JOCHICO, LINA LYN R|F
JOHNSON, RAZI|M
JONSAY, MICHELLE|F
JORDANA, MARIE PERSONA DELGADO|F
JOSON, ANGELA CABAHUG|F
JUDAYAO, FLOSSIE|F
JUMAYAO, CLEMAR JOHN|M
LABIS, ACE DANIELLE|M
LACSON, EMILY|F
LAGANZON, SUSAN|F
LAGOS, LEN|F
SALBINO, ZIERREL FERRER|M
SALCEDO, MA JEE|F
SALGON, MARY GRACE|F
SALIDO, RENSU|F
SALVADOR, ANALYN|F
SALVADOR, JOERINA JALANDO-ON|F
SALVERON, CATHERINE D|F
SALVERON, JOSE|M
SALVERON, MARIA SHEENA|F
SANTE, REGGIE|M
SANTE, RIANNA CASSANDRA|F
SANTE, RONALYN|F
SANTIA, TRISHA ANNE|F
SANTIAGO, CARMELA|F
SANTILLANA, ROSELLE REYES|F
SANTOS, CEREALLE M|F
SANTOS, PAMELA GRACE|F
SANTOS, ROBERTO|M
SARMIENTO, CHRISTINE|F
SASON, REY ANGELO|M
SATO, HITOMI|F
SATO, LOWELL B|M
SATO, VIRGINIA|F
SATELAN, PATRICK|M
SEGOVIA, KRISTINE THERESE|F
SELDA, LIZANY|F
SEMBLANTE, JIMMY|M
SENAPELO, JOSEPH MEDENCELES|M
SENAYO, WINDELLE|F
SERIE, JULIE|F
SERIOS, CATHY|F
SERON, RELYN|F
SESOYRO, CHER RYANNE|F
SILVA, TEODORA|F
SILVESTRE, MERIAM|F
SIMON, KIMBERLY|F
SIMON, RHODA BARCALON|F
SINAMAY, JANELYN Y|F
TUDARA, JAN MARI|F
TUNDAG, KHEA R|F
TUPAS, MARK ANTHONY|M
TUPAS, RHEA JOYCE|F
TY, PHOEBE|F
UNDAR, GLORIA|F
URSOS, CLARISSA|F
UY, CHAVY|M
UY, CLOYD|M
UY, JENNIFER|F
UY, MONIQUE|F
UYCHIAT, RACHEL MARIE VIVERO|F
VALE, KHRIS DANIELLE|F
VALLADAREZ, SIMONETTE ANDRADA|F
VALLESTERO, EMILY|F
VARGAS, CRISELDA|F
VELASCO, ANDREA MARIE|F
VELASCO, ANGELICA|F
VELASCO, ANNA|F
VELASCO, CECILIA|F
VELASCO, NATHAN ELIJAH|M
VELASCO, SIMON|M
VELASCO, SIMON SR|M
VELASCO, YVONNE|F
VELORIA, FRANCINE|F
VENUS, ANDY|M
VENUS, ELIZ|F
VERDE, CYBILL CAROLINE|F
VERDE, RUBY GRACE|F
VILLACARLOS, BEVERLY|F
VILLACARLOS, TOBY|M
VILLACRUSIS, KARL|M
VILLAFLOR, JEFFCY|M
VILLALOBOS, GARCELA|F
VILLANUEVA, NATALIA|F
VILLARIAS, CALVIN|M
VILLARIAS, GLAELYN JOAN|F
VILLARIAS, NOLA|F
VILLARUZ, SHEIRRA|F
VILLASENOR, AMIHAN|F
VILLACRUSIS, JULIETA|F
YALONG, JISSON|M
YAMBOT, MARIA LOURDES DELA CRUZ|F
YAP, ELLA|F
YAP, THEA|F
YBUT, EMILY FAITH|F
YBUT, HYRO|M
YEE, MARY JOY|F
YEE, NELIA|F
YMBALLA, CANDICE BLANCHE|F
YMBALLA, NADINE ASHLEY|F
YMBALLA, PAOLA VANESSA|F
YUSAY, RONEL|M
ZAMORA, ROSALIE ANN|F
ZAPANTA, DAX|M
ZARCENO, MA. CORNELIA|F
ZULETA, FEEVEE|F
ZY, LIZ|F
ABDULA, MARIA ELENA|F
ABETO, ANGELO JESSEN|M
ABETO, JENEVIEVE|F
ABINA, JEZRELL BELIA|F
ABONALES, JO-ANN|F
ABONIL, ANGEL FAITH|F
ABOSO, EDEN|F
ABOSO, EMILY P|F
ABOSO, HANS FRANCIS|M
ACUYADO, PRINZZLE|F
ALAPO, JINLEI|M
ALBA, SURFFY MAE|F
ALEJORA, NOEMI|F
ALIGARVES, RHODORA|F
ALIGUI, DOLORES BUSTAMANTE|F
ALINIO, JOELYN|F
ALISEN, CHRISTINE|F
ALOTENCIO, GERMILYN|F
ALOTENCIO, NOLI|M
ALVARADO, JOSELITO|M
ALVAREZ, JASMIN GRACE|F
AMARA, ARLENE|F
ANDRADA, KHRYSTELLE R|F
ANILADO, RODINA C|F
ANTONIO, MAUREEN BARAOG|F
AQUILLA, ANGELINA|F
ARAULLO, KISINER|F
ARDEVELA, LOVE|F
ARIMBOS, NORMA A|F
ARQUINTILLO, SHENNIA|F
ARRIENDA, JOCELYN|F
ARTIEDA, GERARDO|M
ASTRE, SAMANTHA|F
ATILON, NATASHA|F
ATINGRO, ROSE JANE|F
AURELIO, ANA KATRINA B|F
BAHAGUE, ARSEL JANE|F
BALANGAO, CARMENCITA|F
BALAZUELA, EVANGELINE A|F
BALOLOT, JULIENNE|F
BALSICAS, LILIBETH|F
BALTAZAR, MARIBEL|F
BALTAZAR, WELSITA|F
BANASIG, DESIREE BANILLA|F
BANASIG, PASCUALITO|M
DANIEL, AIDA FE GONZALES|F
BANIEL, ANDREI|M
BANIEL, CHERYL ANNE GONZALES|F
BANOT, APRIL ROSE|F
BANTIGUE, CHAT|F
BANTIGUE, MARIANNE|F
BANTIGUE, MARY ANN|F
BARBO, ANA|F
BARBO, GEMAA|F
BARBOSA, ANN MAGDALENE|F
BARBOSA, TERRENCE|M
BARDOQUIN, KYLA JANE|F
BARILLO III, BENEDICTO|M
BARNIZO, CHARLES|M
BARON, STEFANY|F
BAYER, ANDREI|M
BAYER, MA. THERESA|F
BAYON-ON, NELIA|F
BELECTINA, JOSHUA|M
BELECTINA JR, RONNEL|M
BENDOL, JON LEXUS|M
BENDOL, JUNE ANNE|F
BENIABON, RENZIE SALBINO|M
BENIABON, RYAN|M
BENIGNOS, LEONARDO|M
BENJAMIN, ALVIRA|F
BERANIO, LAILAH|F
BERATIO, RAQUEL|F
BERAYO, GENELLE MONDRAGON|F
BERJIT, APRIL ROSE|F
BERJIT, JOHN EARL|M
CARMONA, KYLA|F
CARMONA, MARY KATE BONCALON|F
CARMONA, ROMELA BONCALON|F
CASIDO, CARMI JOY|F
CASTILLER, JOHANAN|M
CASTILLO, DREIFUZ TEOVIC|M
CASTILLO, JOCILYN|F
CASTILLO, MARIE JHUN MONDEJAR|F
CASTOR, KEVIN|M
CASTOR, MIKHAELA|F
CASTRO, FERNAND|M
CASTRO, IRMA|F
CASTRO, IVAN AUSTINE|M
CASTRO, KEVIN WILLIAM|M
CATAPANG, JOY|F
CELIS, GENETTE|F
CELIS, LEDA|F
CENTERING, MA CHRISTINA|F
CHAUCA, MALOU DELA CRUZ|F
CHAVEZ, ROSALIE|F
CLAVERIA, MIKE|M
CLAVERIA, VIRGINIA F|F
CLAVERIA, WILSON|M
CLELO, CATHERINE|F
CONDING, RENEE|F
CONSTANTINO, SHAIRA|F
CONTE, GLENDA|F
CONTE, JUN REY|M
CONTRERAS, LORENZO|M
CORRAL, EDA|F
COSAS, RAINER CAMBRONERO|M
COSCOS, RAYVEN CAMBRONERO|M
COSCOLLUELA, MIGUEL|M
COSCOLLUELA, TERESA|F
CRISTALES, MIKE|M
CRUZ, RITZ|M
CRUZ, VANCE|M
CURAMMENG, JENNELYN|F
DELA PENA, NEMIA F|F
DELA TORRE, MARIA SABRINA|F
DELA TORRE, MARIA SAMANTHA|F
DELA TORRE, NATHANIEL|M
DELA TORRE, ROLINA|F
DELGADO, ANTON JOHN|M
DELGADO, ANGELIE FRANZ|F
DELGADO, ANTON|M
DELGADO, CARLOS|M
DELGADO, EDNA ELAINE|F
DELGADO, JUANA|F
DELGADO, MAY|F
DELGADO, MELINDA|F
DELGADO, MICHAEL ANGELO|M
DELGADO, SUSAN|F
DESPUIG, JESSA P|F
DEVELA, ELIZABETH|F
DEVELOS, LEANN LORRAINE RAMOS|F
DEWALA, CHRISTINE|F
DIESTO, TYRA L|F
DIEUMANO, EVELYN|F
DILE, BONA|F
DILE, NYK|M
DILE, ROWENA|F
DILE, RYK|M
DIROPON, ATTY ERNESTO|M
DIO, EILEN|F
DIOMAS, DENMART|M
DIVINGACIA, ANGELA|F
DIZON, JEN MAY|F
DIZON, JERUEL IAN|M
DIZON, RIZZA|F
DONARIA, NIÑALIZA|F
DONARIA, JOAN|F
DONARIA, JOJI|F
DONASCO, ABIGAIL|F
DONASCO, AMABELLE VICTORIA|F
EINOSAS, JV SNOOK|M
EINOSAS, KAT|F
EJERCITO, EDERLYN GONZAGA|F
EJERCITO, RITZ|M
ELLAB, MARY ROSE|F
EMBAJADOR, MICHAEL|M
EMBANG, ERIKA|F
ENGRACIA, LOLITA|F
ENTAPAN, JENELYN|F
EPLAGO, MA. CRISTINA JACOLBE|F
ESPERANZA, JELLY MAE|F
ESPELETA, PAUL SEMBRANO|M
ESPIRITU, MAAN|F
ESTRADA, REIN|F
EUGENIO, RONEL ERECE|M
EVANGELISTA, GLANE|F
FAMOSO, KATRINA SHEENA|F
FARENELY, CORNELIO HOPE LEGASPINA|F
FERNANDEZ, CHARLIE|M
FERRER, WILLIE JANE|F
FIRMAN, MA. ANNA FATIMA PALPARAN|F
FOJADO, ALYN|F
FUENTES, KIM|F
GABALLO, KRISTA AINEE|F
GALLEGO, MRS DIANE|F
GALLO, ANDREA BIELLE|F
GALLO, SHARON|F
GALLO, JOHAN NINO M|M
GALLO, JOHANNES NINO|M
GAMBOA, KIM PIAMONTE|F
GARLAD, MOMINA|F
GANZA, GLENN|M
GANZA, MYLENE|F
GARGALLANO, JERYMAY|F
GARTOSE, KATELYN|F
GARZON, CHRISTIAN|M
GRAZON, NEPH|M
GASTON, SHAIRA REYES|F
"""

        # Parse patient names
        patient_names = []
        for line in patient_names_data.strip().split('\n'):
            if '|' in line:
                parts = line.split('|')
                if len(parts) == 2:
                    name_parts = parts[0].split(',', 1)
                    if len(name_parts) == 2:
                        last_name = name_parts[0].strip()
                        first_name = name_parts[1].strip()
                        gender = parts[1].strip()
                        patient_names.append((last_name, first_name, gender))

        # Years for distribution - using 2020-2024 (not 2025 since it's still 2024)
        years = [2020, 2021, 2022, 2023, 2024]
        occupations = [
            "Teacher", "Student", "Nurse", "Engineer", "Accountant", 
            "Business Owner", "Call Center Agent", "Designer", "Driver",
            "Housewife", "Office Worker", "Sales Clerk", "Manager",
            "Social Worker", "Government Employee", "BPO Employee",
            "Architect", "Police Officer", "Seaman", "OFW", "Retired",
            "Civil Engineer", "Lawyer", "Judge", "Virtual Assistant",
            "Private Company", "School Nurse", "Reporter", "Secretary",
            "CSR", "Operation Manager", "Caregiver", "Junior Architect",
            "Accounting Clerk", "Admin Supervisor", "Physician",
            "ESL Teacher", "Research Nurse", "Govt Employee", "Businessman",
            "Event Organizer", "Admin Assistant", "Freelancer", "Banker",
            "Insurance Agent", "Contractor", "Air Traffic Controller",
            "Cake Decorator", "Office Clerk", "Self Employed", "Branch Manager",
            "Customer Relation Officer", "Cabin Crew", "VAVIC Desk Officer",
            "Radtech", "PNP", "BPO Employee", "ESL Tutor"
        ]

        addresses = [
            "Bacolod City", "Silay City", "Talisay City", "Victorias City",
            "Villamonte", "Mandalagan", "Banago, Bacolod City",
            "Capitol Ville", "Villa Angela Subd. Bacolod City",
            "BRGY BATA", "BRGY CABUG", "BRGY VILLAMONTE",
            "Pasay City", "Manila", "Cebu City",
            "BRGY. GRANADA, BACOLOD CITY", "ALTIS, Bacolod City",
            "Fortune Towne, Bacolod City", "Camella Homes",
            "Bago City", "Amaia Scapes", "North Point Ayala",
            "MT View Subdivision", "East Homes 2", "Airport Subd",
            "Villa Angela, B.C", "Brgy Bubog, Talisay City",
            "EB Magalona", "Brgy Punta Taytay", "Singcang, B.C"
        ]

        created_count = 0
        skipped_count = 0

        self.stdout.write(self.style.SUCCESS('Starting patient population...'))
        self.stdout.write(self.style.SUCCESS(f'Total patients to create: {len(patient_names)}'))

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
                    
                    if created_count % 50 == 0:
                        self.stdout.write(self.style.SUCCESS(f'Created {created_count} patients...'))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating {first_name} {last_name}: {str(e)}'))
                    skipped_count += 1
            else:
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {created_count} patients'))
        self.stdout.write(self.style.WARNING(f'⚠️  Skipped {skipped_count} patients (already exist or errors)'))
        self.stdout.write(self.style.SUCCESS('\nPatient distribution by year:'))
        
        for year in [2020, 2021, 2022, 2023, 2024]:
            year_start = datetime(year, 1, 1)
            year_end = datetime(year, 12, 31)
            count = User.objects.filter(
                user_type='patient',
                date_joined__gte=timezone.make_aware(year_start),
                date_joined__lte=timezone.make_aware(year_end)
            ).count()
            self.stdout.write(self.style.SUCCESS(f'  {year}: {count} patients'))
