import helixcore.db.deadlock_detector as deadlock_detector
import helixtariff.domain.objects as objects

deadlock_detector.ALLOWED_TRANSITIONS = [
    (objects.ServiceSet.table, objects.ServiceSetRow.table), #add, modify, delete service set
#    (objects.Balance.table, objects.Balance.table), #lock list
#    (objects.BalanceLock.table, objects.BalanceLock.table), #unlock list
]
