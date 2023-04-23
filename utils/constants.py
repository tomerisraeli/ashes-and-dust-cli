from handlers.local_handlers.distance_to_water_handler import DistanceToWaterHandler

DATE_FORMATS = formats = ["%Y",
                          "%m/%Y", "%m-%Y", "%m.%Y",
                          "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"
                          ]

LOCAL_HANDLERS = [DistanceToWaterHandler()]
DOWNLOAD_HANDLERS = []
