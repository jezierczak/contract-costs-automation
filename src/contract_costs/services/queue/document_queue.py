from queue import Queue

from contract_costs.services.workers.dto.document_process_queue_item import DocumentProcessQueueItem

document_queue: Queue[DocumentProcessQueueItem] = Queue()
