from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

app = Flask(__name__)

# Function to load data
def load_data(filename):
    return pd.read_csv(filename)

# Function to analyze protocol distribution
def analyze_protocol_distribution(df):
    protocol_counts = df['protocol'].value_counts()
    plt.figure(figsize=(10, 6))
    protocol_counts.plot(kind='bar')
    plt.title('Protocol Distribution')
    plt.xlabel('Protocol')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save plot to a BytesIO object to send it to the frontend
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return img_base64

# Function to analyze payload sizes
def analyze_payload_sizes(df):
    plt.figure(figsize=(10, 6))
    sns.histplot(df['total_len'], bins=50, kde=True)
    plt.title('Distribution of Payload Sizes')
    plt.xlabel('Payload Size')
    plt.ylabel('Frequency')
    plt.tight_layout()

    # Save plot to a BytesIO object to send it to the frontend
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return img_base64

# Function to identify anomalies (large payloads)
def identify_anomalies(df):
    # Example: Identify connections with unusually large payloads
    large_payload_threshold = df['total_len'].quantile(0.95)
    anomalies = df[df['total_len'] > large_payload_threshold]
    return anomalies

# Function to analyze time deltas
def analyze_time_deltas(df):
    plt.figure(figsize=(10, 6))
    sns.histplot(df['t_delta'], bins=50, kde=True)
    plt.title('Distribution of Time Deltas')
    plt.xlabel('Time Delta')
    plt.ylabel('Frequency')
    plt.tight_layout()

    # Save plot to a BytesIO object to send it to the frontend
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return img_base64

# Flask route for uploading and analyzing CSV
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        file = request.files['file']
        if file:
            # Load the data
            df = load_data(file)
            
            # Perform analysis
            protocol_img = analyze_protocol_distribution(df)
            payload_img = analyze_payload_sizes(df)
            time_delta_img = analyze_time_deltas(df)
            
            # Identify anomalies
            anomalies = identify_anomalies(df)
            anomalies_img = None
            if not anomalies.empty:
                anomalies_img = anomalies[['t_delta', 'total_len']].plot(kind='scatter', x='t_delta', y='total_len', color='red', figsize=(10, 6))
                plt.title('Anomalies in Network Traffic')
                plt.xlabel('Time Delta')
                plt.ylabel('Total Length')
                plt.tight_layout()

                # Save plot to a BytesIO object to send it to the frontend
                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                anomalies_img = base64.b64encode(img.getvalue()).decode('utf-8')
            
            # Render result page with images
            return render_template('result.html', 
                                   protocol_img=protocol_img, 
                                   payload_img=payload_img, 
                                   time_delta_img=time_delta_img,
                                   anomalies_img=anomalies_img,
                                   table=df.head().to_html())
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)
