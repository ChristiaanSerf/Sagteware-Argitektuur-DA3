from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'db'),  # service name, not localhost
        port=os.getenv('POSTGRES_PORT', '5432'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
        database=os.getenv('POSTGRES_DB', 'cs2')
    )
    return conn


@app.route('/execute_sql', methods=['POST'])
def execute_sql():
    """
    Expects JSON body:
    {
        "query": "SELECT * FROM \"User\" WHERE UserID = %s",
        "params": [1]
    }
    """
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    query = data['query']
    params = data.get('params', [])

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        # Try to fetch results if it's a SELECT
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
            response = {"results": results}
        else:
            conn.commit()
            response = {"rowcount": cur.rowcount}
        cur.close()
        conn.close()
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
