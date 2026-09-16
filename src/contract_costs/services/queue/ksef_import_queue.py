from queue import Queue

from contract_costs.services.workers.dto.ksef_import_queue_item import KsefImportQueueItem

ksef_import_queue: Queue[KsefImportQueueItem] = Queue()
