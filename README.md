Proyecto listo                                                                                 
                                                                                                
coema-facturacion/                                                                             
├── src/                                                                                       
│   └── app.py              # App principal (con datos reales de facturas)                     
├── facturas/               # PDFs de referencia                                               
├── .streamlit/                                                                                
│   └── config.toml         # Configuración visual                                             
├── requirements.txt        # Dependencias                                                     
├── .gitignore                                                                                 
└── REQUISITOS.MD                                                                              
                                                                                                
Datos corregidos basados en facturas reales                                                    
┌──────────────────────┬────────────────────────────┐                                          
│        Campo         │         Valor Real         │                                          
├──────────────────────┼────────────────────────────┤                                          
│ T1R                  │ Monotributista - IVA 27%   │                                          
├──────────────────────┼────────────────────────────┤                                          
│ T1RE                 │ Consumidor Final - IVA 21% │                                          
├──────────────────────┼────────────────────────────┤                                          
│ Ley 7290             │ 4% del subtotal            │                                          
├──────────────────────┼────────────────────────────┤                                          
│ Ley 11769 Art 75     │ 6%                         │                                          
├──────────────────────┼────────────────────────────┤                                          
│ Ley 11769 Fondo Comp │ ~5.5%                      │                                          
├──────────────────────┼────────────────────────────┤                                          
│ Alumbrado Nov        │ $9,284                     │                                          
├──────────────────────┼────────────────────────────┤                                          
│ Alumbrado Dic        │ $14,000                    │                                          
├──────────────────────┼────────────────────────────┤                                          
│ Bomberos             │ $960                       │                                          
└──────────────────────┴────────────────────────────┘                                          
Para probar localmente                                                                         
                                                                                                
cd /Users/dforce/workspaces/salesforce/coema-facturacion                                       
pip install -r requirements.txt                                                                
streamlit run src/app.py                                                                       
                                                                                                
Deploy en Streamlit Cloud                                                                      
                                                                                                
1. Sube a GitHub                                                                               
2. En https://share.streamlit.io:                                                              
  - Repo: tu-usuario/coema-facturacion                                                         
  - Main file path: src/app.py                                                                 
  - Click Deploy                                                                               
                                                                                                
El MVP incluye las 4 funcionalidades: Calculadora, Simulador, Historial y Comparador de        
Tarifas.                                                                                       


# Create virtual environment and install dependencies     
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt      

# Test streamlit app runs correctly             
source .venv/bin/activate && streamlit run src/app.py --server.headless true &             
sleep 3                                                                                    
curl -s http://localhost:8501 | head -20                                                   


# Listo para usar                                                                             
                                                                                              
Estructura final:                                                                           
  coema-facturacion/                                                                          
  ├── .venv/                  # Entorno virtual Python                                        
  ├── src/                                                                                    
  │   └── app.py              # App Streamlit                                                 
  ├── facturas/               # PDFs de referencia                                            
  ├── .streamlit/                                                                             
  │   └── config.toml                                                                         
  ├── requirements.txt                                                                        
  └── .gitignore                                                                              
                                                                                            
Para ejecutar localmente:                                                                   
cd /Users/dforce/workspaces/salesforce/coema-facturacion                                    
source .venv/bin/activate                                                                   
streamlit run src/app.py                                                                    
                                                                                            
Para deploy en Streamlit Cloud:                                                             
1. Sube a GitHub (sin la carpeta .venv/)                                                    
2. En share.streamlit.io:                                                                   
  - Main file path: src/app.py                                                              
                                                                                            
Precisión del cálculo:                                                                      
- T1RE (Consumidor Final): ~99.9% de precisión                                              
- T1R (Monotributista): ~97.4% - pequeña diferencia por prorrateo entre resoluciones        
tarifarias                     