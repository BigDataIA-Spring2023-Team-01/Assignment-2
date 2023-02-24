from diagrams import Diagram
from diagrams import Cluster, Edge, Node
from diagrams.azure.identity import Users
from diagrams.onprem.container import Docker
from diagrams.onprem.workflow import Airflow
from diagrams.aws.storage import SimpleStorageServiceS3 as S3
from diagrams.azure.database import SQLServers 
from diagrams.oci.monitoring import Notifications
from diagrams.azure.general import Helpsupport
from diagrams.gcp.operations import Monitoring
from diagrams.aws.management import Cloudwatch
from diagrams.aws.storage import ElasticBlockStoreEBSSnapshot

with Diagram("Deployment Architecture Diagram", show=False):
    ingress = Users("Developing team 01")
    with Cluster("Docker Compose"):
        with Cluster("App"):
            userfacing = Monitoring("Streamlit")
            backend = Docker("FastAPI")
            

        with Cluster("Sqlite Database"):
            db = SQLServers("SQlite")

        with Cluster("Airflow Process"):
            airflow = Airflow("Airflow")
            GE = Notifications("Meta-Data Check")
            hostings = S3("Quality Check Reports")

        with Cluster("AWS services"):
            cloudwatch = Cloudwatch("AWS Logs")
            bucket = ElasticBlockStoreEBSSnapshot("AWS s3 bucket")
    
    hostings>> Edge(label="GE reports") >> bucket
    backend << Edge(label="APLI Call", color="black") << userfacing
    backend << Edge(label="Logging Verification") << db
    team = Users("Login User")
    metadata = S3("AWS s3 open source buckets")

    # team << Edge("User Interface") << userfacing
    GE >> Edge() >> db
    GE >> Edge(label="static GE html report") >> hostings
    airflow >> Edge(label="GE checkpoints") >> GE

    airflow << Edge(label="Data Collection") << metadata
    airflow >> Edge(label="Updating AWS bucket data periodically") >> bucket

    # cloudwatch >> Edge("Logging actions in AWS cloudwatch") >> airflow
    # hostings>> Edge("GE reports check periodically") >> bucket
