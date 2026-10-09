from models.vector_store import VectorStore
#from services.llm_service import LLMService
from services.chatlite_llm_router import LLMService
from config import Config
from services.storage_service import S3StorageService
import tempfile
import logging
import os
from services.document_loader import DocumentProcessor
from flask import Flask, app, request, jsonify, render_template

app = Flask(__name__)

vector_store = VectorStore(path=Config.VECTOR_DB_PATH)
llm_service = LLMService(vector_store=vector_store.vectore_store)
storage_service = S3StorageService()   

#Configre logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_documents(file):
    """Load, process, and store documents in the vector store."""
    try:
        # Save the uploaded file to a temporary location
        temp_dir = tempfile.mkdtemp()
        temp_file_path = f"{temp_dir}/{file.filename}"
        file.save(temp_file_path)

        document_processor = DocumentProcessor()
        chunks = document_processor.ingest_documents([temp_file_path])
        return chunks
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):  
            os.remove(temp_file_path)
        os.rmdir(temp_dir)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_document():
    try:
        logger.debug("Upload endpoint called")
        
        if 'file' not in request.files:
            logger.warning("No file in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning("Empty filename")
            return jsonify({'error': 'No file selected'}), 400

        # Check file extension
        if not file.filename.endswith(('.txt', '.pdf')):
            logger.warning(f"Unsupported file type: {file.filename}")
            return jsonify({'error': 'Only .txt and .pdf files are supported'}), 400

        logger.debug(f"Processing file: {file.filename}")
        
        # Process the document
        try:
            text_chunks = process_documents(file)
            logger.debug(f"Document processed into {len(text_chunks)} chunks")
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return jsonify({'error': f'Error processing document: {str(e)}'}), 500

        # Upload to S3
        try:
            file.seek(0)  # Reset file pointer
            storage_service.upload_file(file, file.filename)
            logger.debug("File uploaded to S3")
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            return jsonify({'error': f'Error uploading to S3: {str(e)}'}), 500

        # Add to vector store
        try:
            vector_store.add_documents(text_chunks)
            logger.debug("Documents added to vector store")
        except Exception as e:
            logger.error(f"Error adding to vector store: {str(e)}")
            return jsonify({'error': f'Error adding to vector store: {str(e)}'}), 500

        return jsonify({
            'message': 'File uploaded and processed successfully',
            'chunks_processed': len(text_chunks)
        })

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/query', methods=['POST'])
def query():
    data = request.json
    if 'question' not in data:
        return jsonify({'error': 'No question provided'}), 400

    try:
        session_id = "123"#data.get('session_id', 'default_session')
        response = llm_service.generate_response(data['question'], session_id=session_id)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug= True)