# Guia de Instalacion — Sesion 2

## Requisitos del Sistema

- Python 3.10+
- Node.js 18+ y npm
- RAM: minimo 8GB (16GB recomendado para modelos 7B+)
- Espacio en disco: 5GB libres para modelos Ollama
- Sistema operativo: Windows 10/11, macOS 12+, Ubuntu 20.04+

---

## Paso 1 — Instalar Ollama

### Linux / macOS
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
Descargar el instalador desde: https://ollama.com/download/windows

### Verificar instalacion
```bash
ollama --version
# ollama version 0.x.x

# El servicio deberia iniciar automaticamente
# Si no, ejecutar:
ollama serve
```

---

## Paso 2 — Descargar Modelos

```bash
# Modelo recomendado para el aula (2GB, rapido)
ollama pull llama3.2

# Modelo con buen balance calidad/tamano (4GB)
ollama pull mistral

# Modelo ultra liviano (2.3GB)
ollama pull phi3:mini

# Verificar modelos descargados
ollama list
```

---

## Paso 3 — API Keys (Modelos Propietarios)

Crea un archivo `.env` en la carpeta `session_2/`:

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google
GOOGLE_API_KEY=AIza...

# Ollama (local, sin API key)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

**NUNCA** subas este archivo a GitHub. El `.gitignore` ya lo excluye.

Si no tienes API keys de proveedores propietarios, todos los ejemplos
tienen un MODO_SIMULADO que funciona sin credenciales.

---

## Paso 4 — Entorno Python

```bash
cd session_2

# Crear entorno virtual
python -m venv venv

# Activar
source venv/bin/activate          # Linux/macOS
venv\Scripts\activate             # Windows PowerShell

# Instalar dependencias
pip install --upgrade pip setuptools wheel
pip install -r ../requirements.txt

# Verificar
python -c "import openai, anthropic, httpx; print('OK')"
```

---

## Paso 5 — Frontend React

```bash
cd session_2/frontend
npm install
npm run dev
# Abrir http://localhost:5173
```

---

## Solucion de Problemas Comunes

### "Connection refused" al llamar Ollama
```bash
# Verificar que el servicio esta corriendo
curl http://localhost:11434/api/tags

# Si falla, iniciar manualmente
ollama serve
```

### "Model not found" en Ollama
```bash
# Ver modelos disponibles
ollama list

# Descargar el modelo faltante
ollama pull llama3.2
```

### Error de API key invalida
```bash
# Verificar que el .env existe y tiene el valor correcto
cat .env | grep OPENAI_API_KEY
# No debe mostrar el valor en la terminal publica

# El modo simulado funciona sin API key:
MODO_SIMULADO=true python ejemplos/01_modelos_propietarios.py
```

### Error de memoria insuficiente con Ollama
```bash
# Usa un modelo mas pequeno
ollama pull phi3:mini    # Solo 2.3GB
```
