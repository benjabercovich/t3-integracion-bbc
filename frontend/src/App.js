import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState('');

    const handleQuery = async () => {
        try {
            const result = await axios.post('https://t3-integracion-bbc.onrender.com/query', { query });
            setResponse(result.data.response);
        } catch (error) {
            setResponse("Error occurred while querying.");
        }
    };

    return (
        <div style={styles.container}>
            <h1 style={styles.header}>Movie Chatbot</h1>
            <div style={styles.inputContainer}>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask about a movie..."
                    style={styles.input}
                />
                <button onClick={handleQuery} style={styles.button}>Submit</button>
            </div>
            <div style={styles.responseContainer}>
                <h2 style={styles.responseHeader}>Response:</h2>
                <h4 style={styles.responseHeader}>Takes about 1 minute</h4>
                <p style={styles.responseText}>{response}</p>
            </div>
        </div>
    );
}

const styles = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        backgroundColor: '#f0f4f8',
        fontFamily: 'Arial, sans-serif',
        padding: '20px',
    },
    header: {
        fontSize: '2.5rem',
        color: '#333',
        marginBottom: '20px',
    },
    inputContainer: {
        display: 'flex',
        gap: '10px',
        marginBottom: '20px',
    },
    input: {
        width: '300px',
        padding: '10px',
        fontSize: '1rem',
        border: '1px solid #ccc',
        borderRadius: '4px',
        outline: 'none',
    },
    button: {
        padding: '10px 15px',
        fontSize: '1rem',
        color: '#fff',
        backgroundColor: '#007bff',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        transition: 'background-color 0.3s ease',
    },
    buttonHover: {
        backgroundColor: '#0056b3',
    },
    responseContainer: {
        width: '100%',
        maxWidth: '500px',
        textAlign: 'center',
        backgroundColor: '#fff',
        padding: '15px',
        borderRadius: '8px',
        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
    },
    responseHeader: {
        fontSize: '1.5rem',
        color: '#444',
        marginBottom: '10px',
    },
    responseText: {
        fontSize: '1.1rem',
        color: '#555',
    },
};

export default App;
