INDEX_STRING = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            
            .main-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }
            
            .header p {
                color: #666;
                font-size: 1.1rem;
                font-weight: 400;
            }
            
            .controls-container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                position: relative;
                z-index: 10; 
            }
            
            .controls-grid {
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 30px;
                align-items: start;
            }
            
            .control-group {
                display: flex;
                flex-direction: column;
                gap: 10px;
                position: relative;
                z-index: 100;
            }
            
            .control-group.security-control .Select-control {
                min-width: 280px !important;

            }
            
            .control-group.date-control {
                align-items: center;
                flex-direction: column;
                justify-content: space-between;
            }
                        

            .control-label {
                font-weight: 600;
                color: #333;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .control-label.centered {
                justify-content: center;
            }
            
            .date-range-container {
                display: flex;
                flex-direction: column;
                gap: 10px;
                align-items: flex-start;
            }
        
            .date-picker-wrapper {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }            

            .last-update-info {
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border-radius: 12px;
                padding: 15px;
                text-align: center;
                border: 2px solid #e1e8ed;
                min-width: 140px;
                height: fit-content;
                flex-shrink: 0;
            }

            .last-update-icon {
                font-size: 1.5rem;
                color: #667eea;
                margin-bottom: 5px;
            }
            
            .last-update-value {
                font-size: 1.1rem;
                font-weight: 600;
                color: #333;
                margin-bottom: 2px;
            }
            
            .last-update-label {
                font-size: 0.8rem;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .Select-control {
                border: 2px solid #e1e8ed !important;
                border-radius: 12px !important;
                min-height: 50px !important;
                font-size: 1rem !important;
                transition: all 0.3s ease !important;
            }
            
            .Select-control:hover {
                border-color: #667eea !important;
            }
            
            .Select--is-focused .Select-control {
                border-color: #667eea !important;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
            }
            
            .DateInput_input {
                border: 2px solid #e1e8ed !important;
                border-radius: 12px !important;
                height: 50px !important;
                font-size: 1rem !important;
                padding: 0 15px !important;
                transition: all 0.3s ease !important;
            }
            
            .DateInput_input:focus {
                border-color: #667eea !important;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
            }
            
            .DateRangePickerInput {
                border: 2px solid #e1e8ed !important;
                border-radius: 12px !important;
                height: 50px !important;
                transition: all 0.3s ease !important;
            }
            
            .DateRangePickerInput:hover {
                border-color: #667eea !important;
            }
            
            .summary-container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }
            
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            
            .summary-card {
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                transition: transform 0.3s ease;
            }
            
            .summary-card:hover {
                transform: translateY(-5px);
            }
            
            .summary-card-icon {
                font-size: 2rem;
                margin-bottom: 10px;
                color: #667eea;
            }
            
            .summary-card-value {
                font-size: 1.5rem;
                font-weight: 700;
                color: #333;
                margin-bottom: 5px;
            }
            
            .summary-card-label {
                font-size: 0.9rem;
                color: #666;
                font-weight: 500;
            }
            
            .charts-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-bottom: 30px;
            }
            
            .chart-wrapper {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }
            
            .loading-container {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 400px;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                margin: 20px 0;
            }
            
            .loading-spinner {
                width: 50px;
                height: 50px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

        .control-group.last-update-control {
            align-items: center;
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }


        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''