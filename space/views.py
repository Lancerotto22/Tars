from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from registry.models import Customer, Project, Deliverable, Event
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.middleware.csrf import get_token

## AUTHENTICATION (WORKING) ##

# GET /auth/user/ - shows informations about the session
@api_view(["GET"])  
@permission_classes([IsAuthenticated])
def auth_user(request: Request):

    # Get an object user 
    user = request.user

    if not request.user.is_authenticated:
        return Response({
            "error":"Invalid auth token"
        }, status=401)

    return Response({
        "id": user.pk,               
        "username": user.username,    
        "first_name": user.first_name,  
        "last_name": user.last_name,  
        "email": user.email,          
    }, status=200)  

# POST /auth/login/ - entra in una sessione (nel body json vanno inserite le credenziali per poter accedere ai cookie di sessione e tokencsrf) - possibili risposte gestite 200/400/401 ✓
@api_view(["POST"])
@permission_classes([]) # Tutti possono eseguire un login
def auth_login(request: Request):

    # Estrazione username e password dal file body json nella richiesta
    username = request.data.get("username")
    password = request.data.get("password")
    
    # Se non compaiono nel file restituisci un errore con codice 400 Bad Request
    if not username or not password:
        return Response({
            "error": "Username and password are required"
        }, status=400)
    
    # Se al contrario nel body vi sono username e password, si verifica che le credenziali siano corrette attraverso authenticate (gestita da django), se credenziali corrette user = istanza, altrimenti user = None
    user = authenticate(request, username=username, password=password)
    csrf_token = get_token(request)
    # Se credenziali sono corrette, allora restituisci un messaggio di corretta autenticazione con codice 200 OK
    if user is not None:
        login(request, user)

        return Response({
            "token": csrf_token,
            "message": "Login successful!"
        }, status=200)
    
    # Altrimenti restituisci un errore con codice 401 Unauthorized
    else:
        return Response({
            "error": "Invalid username or password"
        }, status=401)

# POST /auth/logout/ - esce dalla sessione corrente (nell'header va il cookie di sessione e tokencsrf, token inserito manualmente per richieste POST, PUT e DELETE) - possibili risposte gestite 200 ✓
@api_view(["POST"])
@permission_classes([IsAuthenticated]) # Per eseguire un logout bisogna essere autenticati (scelta per motivi di sicurezza)
def auth_logout(request: Request):

    # Funzione di django che rimuove utente dalla sessione elimandone relativi cookie di sessione e tokencsrf (su insomnia rimarranno settati i cookie e il token ma non saranno più validi)
    logout(request)

    # Restituisci messaggio di corretto logout con codice 200 OK
    return Response({
        "message": "Successfully log out"
    }, status=200)










## CUSTOMER MANAGEMENT (WORKING) ##

# GET /customers/ - Ottieni tutti i clienti con il numero di progetti associati e il loro id - possibili risposte gestite 200/401 ✓
@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Solo utenti autenticati possono accedere a queste funzionalità
def get_customers(request):
 
    # Controlla se l'utente è autenticato e in caso contrario restituisci errore con codice 401 Unauthorized
    if not request.user.is_authenticated:
        return Response({
            "error":"Invalid auth token"
        }, status=401)

    # Recupera tutti i clienti attraverso la funzione `Customer.objects.all()` che restituisce un queryset (una raccolta di oggetti in django) con tutti gli oggetti della tabella `Customer`
    customers = Customer.objects.all()

    # Crea una lista di dizionari vuota che conterrà i dati relativi ai clienti
    customers_data = []

    # Per ogni cliente nel queryset
    for customer in customers:

        # Conta il numero di progetti associati a questo cliente (funzione di django)
        num_projects = Project.objects.filter(customer=customer).count()
        
        # Crea un dizionario contenente i dati del cliente con il numero di progetti
        customer_data = {
            "name": customer.name,
            "id": customer.id,
            "number_of_projects": num_projects
        }

        # Aggiungi alla lista di dizionari il dizionario appena creato
        customers_data.append(customer_data)

    # Restituisci i dati con codice 200 OK
    return Response(customers_data, status=200)










# GET /customers/{customer}/ - Ottieni informazioni su un cliente specifico in base al nome - possibili risposte gestite 200/401/404 ✓
@api_view(["GET"])
@permission_classes([IsAuthenticated]) # Solo utenti autenticati possono accedere a queste funzionalità
def get_customer_by_name(request, customer):

    # Controlla se l'utente è autenticato e in caso contrario restituisci errore con codice 401 Unauthorized
    if not request.user.is_authenticated:
        return Response({
            "error": "Invalid auth token"
        }, status=401)

    # Blocco try perche possiamo avere due casistiche, l'istanza corrispondente esiste oppure un errore sollevato da django
    try:
        # Cerca il cliente con il nome fornito, se esiste verrà restituita istanza del cliente corrispondente, altrimenti django solleverà l'errore .DoesNotExist
        customer_instance = Customer.objects.get(name=customer)
        
        # Crea una lista vuota per memorizzare i dati dei progetti relativi al cliente
        projects_data = []

        # Recupero l'istanza del progetto del cliente corrispondente
        projects = Project.objects.filter(customer=customer_instance)

        # Per ogni progetto associato all'istanza del cliente corrispondente 
        for project in projects:

            # Conta i deliverables associati al progetto            
            # Crea il dizionario con informazioni relative al cliente
            project_data = {
                "name": project.name,
                "uri": f"https://tars.tinga.io/space/api/v1/customer/{customer}/projects/{project.name}",
                "number_of_deliverables": project.number_of_deliverables,
            }

            # Aggiungi dizionario alla lista creata in precedenza
            projects_data.append(project_data)
        
        # Prepara i dati del cliente con la lista dei progetti
        customer_data = {
            "name": customer_instance.name,
            "id": customer_instance.id,
            "projects": projects_data,
        }
        
        # Restituisco i dati con codice 200 OK
        return Response(customer_data, status=200)
    
    # Se non viene trovato un cliente con il nome specificato, gestisce l'eccezione e restituisce un errore con codice 404 Not Found
    except Customer.DoesNotExist:
        return Response(
            {"error": "Customer not found"
        }, status=404)









# GET /customers/{customer}/projects/{project}/ - Ottieni informazioni relative al progetto di un determinato customer - possibili risposte gestite 200/401/404 ✓
@api_view(["GET"])  
@permission_classes([IsAuthenticated])  # Solo gli utenti autenticati possono accedere a questa funzionalità
def get_project_details(request, customer_name, project_name):

    # Controlla se l'utente è autenticato e in caso contrario restituisci errore con codice 401 Unauthorized
    if not request.user.is_authenticated:
        return Response({
            "error": "Invalid auth token"  
        }, status=401)

    # Recupera il progetto specifico del cliente filtrando sia il nome del cliente che quello del progetto, la funzione restituisce il primo risultato trovato (se condizioni soddisfatte) e in caso contrario None
    project = Project.objects.filter(customer__name=customer_name, name=project_name).first()
    
    # Se il progetto non esiste, restituisci un errore con codice 404 Not Found
    if project is None:
        return Response(
            {"error": "Project not found"
        }, status=404)

    # Recupera tutti i deliverables associati al progetto
    deliverables = Deliverable.objects.filter(project=project)

    # Crea un dizionario con i dettagli del progetto da restituire nella risposta, inizialmente lista di deliverables vuota
    project_details = {
        "name": project.name,  
        "customer": project.customer.name, 
        "id": project.id,  
        "deliverables": []  # Lista vuota che conterrà i dettagli dei deliverables del progetto
    }

    # Per ogni deliverable presenti nei deliverables
    for deliverable in deliverables:

        # Prepara i dati di ogni deliverable
        deliverable_data = {
            "name": deliverable.name,  # Nome del deliverable
            "uri": deliverable.repository,  # URL del repository del deliverable
            "stages": {

                # Dettagli sulla versione di produzione, con il relativo URI di download e configurazione
                "production": {
                    "current_published_version": deliverable.production_version,
                    "last_published_at": deliverable.production_last_published_at,
                    "download_uri": deliverable.production_download_uri,
                    "current_configuration_uri": f"https://tars.iotinga.it/space/api/v1/customers/{customer_name}/projects/{project_name}/delivered/{deliverable.name}/configurations/production"
                },
                
                # Dettagli sulla versione di staging
                "staging": {
                    "current_published_version": deliverable.staging_version,
                    "last_published_at": deliverable.staging_last_published_at,
                    "download_uri": deliverable.staging_download_uri,
                    "current_configuration_uri": f"https://tars.iotinga.it/space/api/v1/customers/{customer_name}/projects/{project_name}/delivered/{deliverable.name}/configurations/staging"
                },

                # Dettagli sulla versione di delivery
                "delivery": {
                    "current_published_version": deliverable.delivery_version,
                    "last_published_at": deliverable.delivery_last_published_at,
                    "download_uri": deliverable.delivery_download_uri,
                    "current_configuration_uri": f"https://tars.iotinga.it/space/api/v1/customers/{customer_name}/projects/{project_name}/delivered/{deliverable.name}/configurations/delivery"
                }
            },
            
            # Dettagli sull'evento dell'ultimo build
            "last_build_event": {
                "id": deliverable.last_build_event_id,  # ID dell'evento dell'ultimo build
                "outcome": deliverable.last_build_outcome,  # Risultato dell'ultimo build (ad esempio "success", "failure")
                "timestamp": deliverable.last_build_timestamp,  # Data e ora dell'ultimo build
                "type": "build",  # Tipo di evento (presumibilmente sempre 'build')
                "stage": deliverable.last_build_stage,  # Fase dell'ultimo build (es. "compiling", "testing")
                "version": deliverable.last_build_version,  # Versione dell'ultimo build
                "source_code_uri": deliverable.source_code_uri,  # URI del codice sorgente
                "external_ref": deliverable.external_ref,  # Riferimento esterno (se presente)
                "external_ref_uri": deliverable.external_ref_uri  # URI del riferimento esterno (se presente)
            },
            
            # Sezione trascurabile perchè specificate in precedenza
            "repository_uri": deliverable.repository,  # URI del repository del deliverable
            "project": project_name,  # Nome del progetto a cui il deliverable appartiene
            "customer": customer_name  # Nome del cliente a cui il progetto appartiene
        }

        # Aggiungi i dati del deliverable alla lista dei deliverables nel dizionario `project_details`
        project_details["deliverables"].append(deliverable_data)

    # Restituisci i dati con codice 200 OK
    return Response(project_details, status=200)  










# GET /customers/{customer}/projects/{project}/deliverables/{deliverable}/ - Ottieni informazioni su un deliverable di un progetto di un customer - possibili risposte gestite 200/401/404 ✓
@api_view(["GET"])  
@permission_classes([IsAuthenticated])  # Solo gli utenti autenticati possono accedere a questa funzionalità
def get_deliverable_details(request, customer_name, project_name, deliverable_name):
    
    # Controlla se l'utente è autenticato e in caso contrario restituisci errore con codice 401 Unauthorized
    if not request.user.is_authenticated:
        return Response({
            "error": "Invalid auth token"  
        }, status=401)
    
    # Trova il deliverable specifico filtrando per nome customer, nome progetto e nome deliverable, la funzione get_object_or_404 se non trova il deliverable corrispondente, solleva automaticamente un'eccezione di errore con codice 404 Not Found
    deliverable = get_object_or_404(Deliverable, project__customer__name=customer_name,  project__name=project_name,  name=deliverable_name)
    
    # Costruisci la risposta, includendo tutti i dettagli del deliverable
    deliverable_details = {
        "name": deliverable.name,  # Nome del deliverable
        "project": deliverable.project.name,  # Nome del progetto a cui appartiene il deliverable
        "customer": deliverable.project.customer.name,  # Nome del cliente a cui appartiene il progetto
        "id": str(deliverable.id),  # ID del deliverable convertito in stringa per evitare possibili problemi di serializzazione
        "stages": {
            
            # Dettagli sullo stadio di produzione del deliverable
            "production": {
                "current_published_version": deliverable.production_version,  # Versione attualmente pubblicata in produzione
                "last_published_at": deliverable.production_last_published_at,  # Data dell'ultima pubblicazione in produzione
                "download_uri": deliverable.production_download_uri,  # URI per il download della versione di produzione
                "current_configuration_uri": f"https://tars.iotinga.it/space/api/v1/customers/{customer_name}/projects/{project_name}/deliverables/{deliverable.name}/configurations/production"
                # URI della configurazione di produzione
            },
            
            # Dettagli sullo stadio di staging del deliverable
            "staging": {
                "current_published_version": deliverable.staging_version,  # Versione attualmente pubblicata in staging
                "last_published_at": deliverable.staging_last_published_at,  # Data dell'ultima pubblicazione in staging
                "download_uri": deliverable.staging_download_uri,  # URI per il download della versione di staging
                "current_configuration_uri": f"https://tars.iotinga.it/space/api/v1/customers/{customer_name}/projects/{project_name}/deliverables/{deliverable.name}/configurations/staging"
                # URI della configurazione di staging
            },
            
            # Dettagli sullo stadio di delivery del deliverable
            "delivery": {
                "current_published_version": deliverable.delivery_version,  # Versione attualmente pubblicata in delivery
                "last_published_at": deliverable.delivery_last_published_at,  # Data dell'ultima pubblicazione in delivery
                "download_uri": deliverable.delivery_download_uri,  # URI per il download della versione di delivery
                "current_configuration_uri": f"https://tars.iotinga.it/space/api/v1/customers/{customer_name}/projects/{project_name}/deliverables/{deliverable.name}/configurations/delivery"
                # URI della configurazione di delivery
            }
        },
        
        # Un campo per indicare se il deliverable può essere pubblicato dalla UI (qui viene impostato sempre su True)
        "can_publish_from_ui": True,  # Supponiamo che sia sempre True
        "latest_build_events": [
            {
                "id": deliverable.last_build_event_id,  # ID dell'evento dell'ultimo build
                "outcome": deliverable.last_build_outcome,  # Risultato dell'ultimo build (ad esempio "success", "failure")
                "timestamp": deliverable.last_build_timestamp,  # Data e ora dell'ultimo build
                "type": "build",  # Tipo di evento (presumibilmente sempre "build")
                "stage": deliverable.last_build_stage,  # Fase dell'ultimo build (es. "compiling", "testing")
                "version": deliverable.last_build_version,  # Versione dell'ultimo build
                "source_code_uri": deliverable.source_code_uri,  # URI del codice sorgente
                "external_ref": deliverable.external_ref,  # Riferimento esterno (se presente)
                "external_ref_uri": deliverable.external_ref_uri  # URI del riferimento esterno (se presente)
            }
        ],
        
        # URI del repository del deliverable
        "repository_uri": deliverable.repository  # URI del repository del deliverable
    }
    
    # Restituisci i dati con codice 200 OK
    return Response(deliverable_details, status=200)










# GET /deliverables/ - Ottieni tutti i deliverables con informazioni associate - possibili risposte gestite 200/401/404 ✓
@api_view(["GET"]) 
@permission_classes([IsAuthenticated])  # Solo gli utenti autenticati possono accedere a questa funzionalità
def get_all_deliverables(request):
    
    # Controlla se l'utente è autenticato e in caso contrario restituisci errore con codice 401 Unauthorized
    if not request.user.is_authenticated:
        return Response({
            "error": "Invalid auth token"  
        }, status=401)

    # Recupera tutti i deliverables senza alcun filtro
    deliverables = Deliverable.objects.all()

    # Se non ci sono deliverables, restituisci un errore 404 Not Found
    if not deliverables:
        return Response({
            "error": "No deliverables found"
        }, status=404)

    # Costruisce la lista di deliverables da restituire
    deliverable_list = []
    
    # Per ogni deliverable presente
    for deliverable in deliverables:
        # Prepara i dati del deliverable in un dizionario
        deliverable_data = {
            "name": deliverable.name,  # Nome del deliverable
            "project": deliverable.project.name,  # Nome del progetto associato
            "customer": deliverable.project.customer.name,  # Nome del cliente associato al progetto
            "id": str(deliverable.id),  # ID del deliverable (convertito in stringa per evitare problemi di serializzazione)
            "stages": {  
                
                # Dettagli sullo stadio di produzione
                "production": {
                    "status": deliverable.stage_status["production"],
                    "current_published_version": deliverable.production_version,  # Versione attuale in produzione
                    "last_published_at": deliverable.production_last_published_at,  # Data dell'ultima pubblicazione in produzione
                    "download_uri": deliverable.production_download_uri,  # URI per il download della versione di produzione
                    "current_configuration_uri": f"https://tars.iotinga.it/space/api/v1/customers/{deliverable.project.customer.name}/projects/{deliverable.project.name}/deliverables/{deliverable.name}/configurations/production"
                },
                
                # Dettagli sullo stadio di staging
                "staging": {
                    "status": deliverable.stage_status["staging"],
                    "current_published_version": deliverable.staging_version,  # Versione attuale in staging
                    "last_published_at": deliverable.staging_last_published_at,  # Data dell'ultima pubblicazione in staging
                    "download_uri": deliverable.staging_download_uri,  # URI per il download della versione di staging
                    "current_configuration_uri": f"https://tars.iotinga.it/space/api/v1/customers/{deliverable.project.customer.name}/projects/{deliverable.project.name}/deliverables/{deliverable.name}/configurations/staging"
                },
                
                # Dettagli sullo stadio di delivery
                "delivery": {
                    "status": deliverable.stage_status["delivery"],
                    "current_published_version": deliverable.delivery_version,  # Versione attuale in delivery
                    "last_published_at": deliverable.delivery_last_published_at,  # Data dell'ultima pubblicazione in delivery
                    "download_uri": deliverable.delivery_download_uri,  # URI per il download della versione di delivery
                    "current_configuration_uri": f"https://tars.iotinga.it/space/api/v1/customers/{deliverable.project.customer.name}/projects/{deliverable.project.name}/deliverables/{deliverable.name}/configurations/delivery"
                }
            },
            
            "can_publish_from_ui": True,  # Indica se il deliverable può essere pubblicato dalla UI, qui sempre impostato su True
            "latest_build_events": [  # Dettagli sull'ultimo evento di build relativo al deliverable
                {
                    "id": deliverable.last_build_event_id,  # ID dell'ultimo evento di build
                    "outcome": deliverable.last_build_outcome,  # Esito dell'ultimo build (successo, fallimento, etc.)
                    "timestamp": deliverable.last_build_timestamp,  # Timestamp dell'ultimo evento di build
                    "type": "build",  # Tipo di evento (presumibilmente sempre di tipo "build")
                    "stage": deliverable.last_build_stage,  # Fase dell'ultimo build (es. "compiling", "testing")
                    "version": deliverable.last_build_version,  # Versione dell'ultimo build
                    "source_code_uri": deliverable.source_code_uri,  # URI del codice sorgente
                    "external_ref": deliverable.external_ref,  # Riferimento esterno (se presente)
                    "external_ref_uri": deliverable.external_ref_uri  # URI del riferimento esterno (se presente)
                }
            ],

            "repository_uri": deliverable.repository  # URI del repository del deliverable
        }

        # Recupero la configurazione per il deliverable (se disponibile)
        configuration = deliverable.stage_status.get("configuration", {})
        
        # Aggiungo la configurazione alla risposta, se presente
        deliverable_data["configuration"] = configuration

        # Aggiunge i dati del deliverable alla lista
        deliverable_list.append(deliverable_data)

    # Restituisci i dati con codice 200 OK
    return Response(deliverable_list, status=200)










# GET,POST,DELETE /customers/{customer}/projects/{project}/deliverables/{deliverable}/configurations/{stage}/ - Ottieni/Modifica/Elimina lo stato di uno stage di un deliverable (nel dizionario configuration) - possibili risposte gestite 200/401/404/400 ✓
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])  # Solo gli utenti autenticati possono accedere a questa funzionalità
def stage_status(request, customer, project, deliverable, stage):

    # Controlla se l'utente è autenticato e in caso contrario restituisci errore con codice 401 Unauthorized
    if not request.user.is_authenticated:
        return Response({
            "error": "Invalid auth token"
        }, status=401)
    
    # Ottieni il deliverable filtrando in base al nome deliverable, nome progetto, nome customer e in caso non ci fosse restituisco errore con codice 404 Not Found
    deliverable_instance = get_object_or_404(Deliverable, name=deliverable, project__name=project, project__customer__name=customer)
    
    # Recupero configurazioni dal dizionario stage_status
    configuration = deliverable_instance.stage_status.get("configuration")

    # Se non esiste la configurazione restituisco errore con codice 404 Not Found
    if configuration is None:
        return Response({
            "error": "Configuration not found"
        }, status=404)

    # Recupero stage della configurazione
    stage_configuration = configuration.get(stage)

    # Se non esiste restituisco errore con codice 404 Not Found
    if stage_configuration is None:
        return Response({
            "error": f"Stage {stage} in configuration not found."
        }, status=404)


    # Gestisci la richiesta GET per ottenere lo stato dello stage
    if request.method == "GET":

        # Creo dizionario da restituire successivamente con informazioni sullo stage e il suo status
        response = {
            "stage": stage,
            "status": stage_configuration
        }

        # Restituisci i dati con codice 200 OK
        return Response(response, status=200)
    

    # Gestisci la richiesta PUT per modificare lo stato dello stage
    elif request.method == "PUT":
        
        # Carica i dati dal body della richiesta
        data = request.data

        # Ottieni il nuovo stato dal corpo della richiesta
        new_status = data.get("status")
        # Variabile old_status inizializzata solo per comodità e rappresenta l'attuale stato dello stage in configuration
        old_status = stage_configuration  

        # Se non è stato inserito un nuovo stato nel body, restituisci errore 400 Bad Request
        if not new_status:
            return Response({
                "error": "Status is required in the request body."
            }, status=400)

        # Se il vecchio stato è uguale a quello nuovo, restituisci messaggio con codice 200 OK
        if old_status == new_status:
            return Response({
                "message": f"No changes have been applied, stage {stage} is already set {old_status} in configuration."
            }, status=200)

        # Aggiorna lo stato dello stage specificato nel campo `configuration`
        configuration[stage] = new_status
        # Aggiorna l'istanza del deliverable con la configurazione aggiornata
        deliverable_instance.stage_status["configuration"] = configuration
        # Salva l'istanza del deliverable con modifica effettuata
        deliverable_instance.save()

        # Genera una risposta
        response = {
            "message": "Changes have been applied successfully",
            "stage": stage,
            "old_status": old_status,
            "new_status": new_status
        }

        # Restituisci dati con codice 200 OK
        return Response(response, status=200)
    

    # Gestisci la richiesta DELETE per eliminare lo stato dello stage
    elif request.method == "DELETE":

        # Rimuovi lo stato dello stage specificato dalla configurazione
        del configuration[stage]
        deliverable_instance.stage_status["configuration"] = configuration
        # Salva l'istanza del deliverable aggiornato
        deliverable_instance.save()

        # Restituisci risposta con codice 200 OK 
        return Response({
            "message": f"Stage {stage} in configuration has been deleted successfully."
        }, status=200)















    
## TESTING ##

# Da controllare la logica degli events, cosa sono e cosa si deve visualizzare a schermo?
# GET /customers/{customer}/projects/{project}/deliverables/{deliverable}/events/ - Ottieni gli eventi di un deliverable - possibili risposte gestite 200/401/404
@api_view(['GET'])
@permission_classes([IsAuthenticated])# Solo gli utenti autenticati possono accedere a questa funzionalità
def get_deliverable_events(request, customer, project, deliverable):

    # Controlla se l'utente è autenticato e in caso contrario restituisci errore con codice 401 Unauthorized
    if not request.user.is_authenticated:
        return Response({
            "error": "Invalid auth token"
        }, status=401)

    # Recupera i parametri di query
    from_time = request.query_params.get('from', None)
    to_time = request.query_params.get('to', None)
    limit = request.query_params.get('limit', None)
    offset = request.query_params.get('offset', None)

    # Impostare i valori di default
    limit = int(limit) if limit else 50  # Limite di eventi da restituire (default 50)
    offset = int(offset) if offset else 0  # Offset per saltare gli eventi (default 0)

    # Converti "from" e "to" in oggetti datetime, se sono presenti
    from_datetime = datetime.fromisoformat(from_time) if from_time else None
    to_datetime = datetime.fromisoformat(to_time) if to_time else None

    try:
        # Ottieni il deliverable
        deliverable_obj = Deliverable.objects.get(name=deliverable, project__name=project, project__customer__name=customer)

        # Filtra gli eventi in base ai parametri forniti
        events_query = Event.objects.filter(deliverable=deliverable_obj)

        if from_datetime:
            events_query = events_query.filter(timestamp__gte=from_datetime)
        if to_datetime:
            events_query = events_query.filter(timestamp__lte=to_datetime)

        # Paginazione
        events_query = events_query[offset:offset+limit]

        # Serializzazione degli eventi
        events = [{
            "id": event.id,
            "outcome": event.outcome,
            "timestamp": event.timestamp.isoformat(),
            "type": event.type,
            "stage": event.stage,
            "version": event.version,
            "source_code_uri": event.source_code_uri,
            "external_ref": event.external_ref,
            "external_ref_uri": event.external_ref_uri
        } for event in events_query]

        # Risposta 200 con gli eventi
        return Response(events, status=status.HTTP_200_OK)

    except Deliverable.DoesNotExist:
        return Response({"detail": "Deliverable not found"}, status=status.HTTP_404_NOT_FOUND)


# Rende solamente uno stato di uno stage in configuration uguale a published ma effettivamente non pubblica niente 
# POST /customers/{customer}/projects/{project}/deliverables/{deliverable}/publish/ - Rende lo stato di un deliverable uguale a published - possibili risposte gestite 200/401/404
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Solo gli utenti autenticati possono accedere a questa funzionalità
def publish_deliverable(request, customer, project, deliverable):
    
    # Controlla se l'utente è autenticato e in caso contrario restituisci errore con codice 401 Unauthorized
    if not request.user.is_authenticated:
        return Response({
            "error": "Invalid auth token"
        }, status=401)
    
    # Carica i dati dal body della richiesta
    data = request.data

    # Ottieni lo stage da modificare dal corpo della richiesta
    stage = data.get("stage")
    # Ottieni la versione dalla richiesta
    version = data.get("version")

    # Se non è stato inserito lo stage e la versione nel body, restituisci errore con codice 400 Bad Request
    if not stage or not version:
        return Response({
            "error": "Stage and version are required in the request body."
        }, status=400)

    # Ottieni il deliverable in base al nome del deliverable, del progetto e del cliente
    deliverable_instance = get_object_or_404(Deliverable, name=deliverable, project__name=project, project__customer__name=customer)

    # Recupero configurazioni dal dizionario stage_status
    configuration = deliverable_instance.stage_status.get("configuration")

    # Se non esiste la configurazione, restituisci errore con codice 404 Not Found
    if configuration is None:
        return Response({
            "error": "Configuration not found."
        }, status=404)

    # Verifica se lo stato dello stage inserito è già settato "published" e in caso si verifichi questa condizione restituisci messaggio con codice 200 OK
    if configuration.get(stage) == "published":
        return Response({
            "message": f"Stage {stage} is already set published."
        }, status=200)

    # Se lo stage si trova in configuration allora modifica solo lo stato dello stage specificato nella richiesta
    if stage in configuration:
        configuration[stage] = "published"

    # Altrimenti in caso non si trovasse in configuration restituisci errore con codice 404 Not Found
    else:
        return Response({
            "error": f"Stage {stage} not found in configuration."
        }, status=404)

    # Aggiorna la configurazione all'interno di stage_status e salva l'istanza
    deliverable_instance.stage_status["configuration"] = configuration
    deliverable_instance.save()

    # Crea risposta con informazioni sulla pubblicazione
    response = {
        "id": deliverable_instance.id,  # ID unico dell'istanza
        "outcome": "success",  # Esito dell'operazione
        "timestamp": datetime.utcnow().isoformat(),  # Tempo dell'operazione
        "type": "build",
        "stage": stage,
        "version": version,
        "configuration": configuration,  # Configurazione aggiornata
        "deliverable_name": deliverable_instance.name,  # Nome del deliverable
        "deliverable_description": getattr(deliverable_instance, 'description', "No description available"),  # Descrizione del deliverable
        "created_at": deliverable_instance.created_at.isoformat() if hasattr(deliverable_instance, 'created_at') else None,  # Data di creazione
        "updated_at": deliverable_instance.updated_at.isoformat() if hasattr(deliverable_instance, 'updated_at') else None  # Data dell'ultimo aggiornamento
    }

    # Restituisci dati con codice 200 OK
    return Response(response, status=200)


