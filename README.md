@'

\# Swytchcode × OpenF1 Integration



A custom local Swytchcode provider integrating the OpenF1 REST API to retrieve Formula 1 race sessions and driver information.



\## Overview



This project demonstrates how to create, configure, register and execute custom API methods using Swytchcode.



Instead of making HTTP requests directly from Python, the application invokes registered Swytchcode methods through the CLI.



\## Architecture



Python Application

&#x20;   ↓

Swytchcode CLI

&#x20;   ↓

Custom OpenF1 Provider

&#x20;   ↓

OpenF1 REST API



\## Implemented Methods



\### 1. openf1.sessions.list



\- HTTP Method: GET

\- Endpoint: `/sessions`

\- Parameters: `year`, `session\_name`

\- Purpose: Retrieve race sessions for a selected F1 season.



\### 2. openf1.drivers.list



\- HTTP Method: GET

\- Endpoint: `/drivers`

\- Parameter: `session\_key`

\- Purpose: Retrieve drivers for a selected race session.



\## Swytchcode Implementation



The custom provider is located inside:



`.swytchcode/integrations/OpenF1/openf1/1.0.0/`



It contains:



\- `methods.json`: Method definitions and canonical IDs.

\- `wrekenfile.yaml`: HTTP configurations, inputs and execution settings.

\- `manifest.json`: Provider endpoint configuration.



\## Python Integration



The Python application uses `subprocess` to invoke Swytchcode CLI commands and `json` to parse their responses.



Python does not directly call the OpenF1 API.



\## Technologies



\- Python

\- Swytchcode CLI

\- Wrekenfile

\- JSON

\- REST API

\- OpenF1 API



\## Running the Project



From the project directory:



```powershell

python .\\openf1\_demo.py

