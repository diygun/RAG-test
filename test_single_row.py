import psycopg2

try:
    conn = psycopg2.connect("postgresql://rag_user:rag_password@localhost:5432/rag_db")
    with conn:
        with conn.cursor() as cur:

            test_vector = [0.0] * 384

            insert_sql = """
            INSERT INTO document_chunks
            (id, title, department, allowed_roles, content, test_query, expected_answer, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """

            test_data = (
                123,
                "Memo Title",
                "Engineering",
                ["Manager", "Executive"],
                "This is a test doc",
                "Does the test working ?",
                "Yes",
                test_vector
            )

            cur.execute(insert_sql, test_data)
            print("Data inserted successfully !")
            
            cur.execute("SELECT id, title, allowed_roles FROM document_chunks WHERE id = 123;")
            row = cur.fetchone()
            
            print("Read back row from db :")
            print("\tID:", row[0])
            print("\tTitle:", row[1])
            print("\tAllowed Roles:", row[2])
            
            cur.execute("DELETE FROM document_chunks WHERE id = 123;")
            print("Test data cleanned.")
            




except Exception as e:
    print(f"An error occured : {e}")

finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Db connection closed")