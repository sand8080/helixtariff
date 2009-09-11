import helixcore.db.deadlock_detector as deadlock_detector
import helixtariff.domain.objects as objects

deadlock_detector.ALLOWED_TRANSITIONS = [
#    (objects.Balance.table, objects.BalanceLock.table), #unlock, chargeoff
#    (objects.Balance.table, objects.Balance.table), #lock list
#    (objects.BalanceLock.table, objects.BalanceLock.table), #unlock list
]
