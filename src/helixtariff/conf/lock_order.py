import helixcore.db.deadlock_detector as deadlock_detector
#from helixtariff.db.dataobject import ServiceSet, ServiceSetRow


deadlock_detector.ALLOWED_TRANSITIONS = [
#    (ServiceSet.table, ServiceSetRow.table), #add, modify, delete service set
]
