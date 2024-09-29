import uuid
from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from irpf import Usuario
 

app = FastAPI()

# Setting up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Pydantic model for input validation
class UserInput(BaseModel):
    name: str
    bruto: float = Field(..., ge=0, description="Bruto salary must be non-negative")
    tributación_conjunta: bool
    numero_de_hijos: int = Field(..., ge=0, description="Number of children must be non-negative")
    menores_de_3_años: int = Field(..., ge=0, description="Number of children under 3 must be non-negative")

# SQLAlchemy model for database
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    bruto = Column(Float)
    neto = Column(Float)
    mensualidad = Column(Float)
    impuestos = Column(Float)

# Create the database table
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to extract form data and map it to Pydantic model
def get_user_input(
    name: str = Form(...), 
    bruto: float = Form(...), 
    tributacion_conjunta: bool = Form(...), 
    numero_de_hijos: int = Form(...), 
    menores_de_3_años: int = Form(0)  # Default value set to 0
):
    # Backend validation: if numero_de_hijos is 0, set menores_de_3_años to 0
    if numero_de_hijos == 0:
        menores_de_3_años = 0
    
    return UserInput(
        name=name,
        bruto=bruto, 
        tributación_conjunta=tributacion_conjunta, 
        numero_de_hijos=numero_de_hijos, 
        menores_de_3_años=menores_de_3_años
    )

# Root endpoint to serve the HTML form
@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Route to handle form submissions and perform validation
@app.post("/calculate/", response_class=HTMLResponse)
def calculate_salary(request: Request, data: UserInput = Depends(get_user_input), db: SessionLocal = Depends(get_db)):
    # Generate a unique ID for each user request
    unique_id = str(uuid.uuid4())
    
    # Create the Usuario object using the validated Pydantic model
    user = Usuario(data.bruto, data.tributación_conjunta, data.numero_de_hijos, data.menores_de_3_años)

    # Store the result in the database
    db_user = User(
        id=unique_id,
        name=data.name,
        bruto=user.bruto,
        neto=float(user.neto),
        mensualidad=float(user.mensualidad),
        impuestos=float(user.impuestos)
    )
    db.add(db_user)
    db.commit()

    # Display the result in the HTML template
    return templates.TemplateResponse("form.html", {
        "request": request,
        "bruto": user.bruto,
        "neto": user.neto,
        "impuestos": user.impuestos,
        "mensualidad": user.mensualidad
    })

# This block ensures that Uvicorn runs your app on the specified port
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Use 8000 for local development
    uvicorn.run(app, host="0.0.0.0", port=port)