from winter.messaging.messaging_config import MessagingConfig

topology_config = MessagingConfig(
    topics={'sample-producer-topic'},
    consumers={
        'consumer_correct': {'tests.winter_messaging.app_sample.consumer_correct'},
        'consumer_slow': {'tests.winter_messaging.app_sample.consumer_slow'},
        'consumer_with_bug': {'tests.winter_messaging.app_sample.consumer_with_bug'},
    }
)
