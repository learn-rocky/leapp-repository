from leapp.snactor.fixture import current_actor_context
# from leapp.models import RpmTransactionTasks, InstalledRPM, RPM


def test_actor_execution(current_actor_context):

    current_actor_context.run()
    #assert current_actor_context.consume(RpmTransactionTasks)
    #assert len(current_actor_context.consume(RpmTransactionTasks)) == 1
    #assert len(current_actor_context.consume(RpmTransactionTasks)[0].to_install) > 0
    #assert len(current_actor_context.consume(RpmTransactionTasks)[0].to_remove) > 0
    #assert len(current_actor_context.consume(RpmTransactionTasks)[0].to_keep) == 0

