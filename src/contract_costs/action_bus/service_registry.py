# class ServiceRegistry:
#
#     def __init__(self):
#         self._services: dict[type, object] = {}
#
#     def register(self, command_type: type, service) -> None:
#         self._services[command_type] = service
#
#     def get(self, command_type: type):
#         service = self._services.get(command_type)
#         if not service:
#             raise ValueError(f"No service registered for {command_type}")
#         return service
