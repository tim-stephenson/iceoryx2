from . import BackpressureStrategy, Duration, FileName, FilePath, Path
from typing import final

__all__ = ["Blackboard", "Config", "Defaults", "Event", "Global", "Node", "PublishSubscribe", "RequestResponse", "Service", "default", "default_config_file_name", "default_config_file_path", "default_user_config_file_path", "from_file", "from_toml", "global_config", "into_toml", "relative_config_path", "setup_global_config_from_file"]

@final
class Blackboard:
    """
    Default settings for the blackboard messaging pattern. These settings are used unless
    the user specifies custom QoS or port settings.
    """
    def __str__(self, /) -> str: ...
    @property
    def max_nodes(self, /) -> int:
        """
        The maximum amount of supported `iceoryx2.Node` instances. Defines indirectly how many
        processes can open the service at the same time.
        """
    @max_nodes.setter
    def max_nodes(self, /, value: int) -> None:
        """
        Set the maximum amount of supported `iceoryx2.Node` instances.
        """
    @property
    def max_readers(self, /) -> int:
        """
        The maximum amount of supported `Reader` ports
        """
    @max_readers.setter
    def max_readers(self, /, value: int) -> None:
        """
        Set the maximum amount of supported `Reader` ports
        """

@final
class Config:
    """
    Represents the configuration that iceoryx2 will utilize. It is divided into two sections:
    the [Global] settings, which must align with the iceoryx2 instance the application intends to
    join, and the [Defaults] for communication within that iceoryx2 instance. The user has the
    flexibility to override both sections.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @property
    def defaults(self, /) -> Defaults:
        """
        Returns the `Defaults` part of the config
        """
    @property
    def global_cfg(self, /) -> Global:
        """
        Returns the `Global` part of the config
        """

@final
class Defaults:
    """
    Default settings. These values are used when the user in the code does not specify anything
    else.
    """
    def __str__(self, /) -> str: ...
    @property
    def blackboard(self, /) -> Blackboard:
        """
        Returns the blackboard part of the default settings
        """
    @property
    def event(self, /) -> Event:
        """
        Returns the event part of the default settings
        """
    @property
    def publish_subscribe(self, /) -> PublishSubscribe:
        """
        Returns the publish_subscribe part of the default settings
        """
    @property
    def request_response(self, /) -> RequestResponse:
        """
        Returns the request_response part of the default settings
        """

@final
class Event:
    """
    Default settings for the event messaging pattern. These settings are used unless
    the user specifies custom QoS or port settings.
    """
    def __str__(self, /) -> str: ...
    @property
    def deadline(self, /) -> Duration:
        """
        Defines the maximum allowed time between two consecutive notifications. If a notification
        is not sent after the defined time, every `Listener`
        that is attached to a `WaitSet` will be notified.
        """
    @deadline.setter
    def deadline(self, /, value: Duration) -> None:
        """
        Sets the deadline of the event service.
        """
    def disable_notifier_created_event(self, /) -> None:
        """
        Do not emit an event whenever a notifier was created.
        """
    def disable_notifier_dead_event(self, /) -> None:
        """
        Do not emit an event whenever a notifier was identified as dead.
        """
    def disable_notifier_dropped_event(self, /) -> None:
        """
        Do not emit an event whenever a notifier was dropped.
        """
    @property
    def event_id_max_value(self, /) -> int:
        """
        The largest event id supported by the event service
        """
    @event_id_max_value.setter
    def event_id_max_value(self, /, value: int) -> None:
        """
        Set the largest event id supported by the event service
        """
    @property
    def has_notifier_created_event(self, /) -> bool:
        """
        Returns true if the notifier created event was set, otherwise false.
        """
    @property
    def has_notifier_dead_event(self, /) -> bool:
        """
        Returns true if the notifier dead event was set, otherwise false.
        """
    @property
    def has_notifier_dropped_event(self, /) -> bool:
        """
        Returns true if the notifier dropped event was set, otherwise false.
        """
    @property
    def max_listeners(self, /) -> int:
        """
        The maximum amount of supported `Listener`
        """
    @max_listeners.setter
    def max_listeners(self, /, value: int) -> None:
        """
        Set the maximum amount of supported `Listener`
        """
    @property
    def max_nodes(self, /) -> int:
        """
        The maximum amount of supported `iceoryx2.Node` instances. Defines indirectly how many
        processes can open the service at the same time.
        """
    @max_nodes.setter
    def max_nodes(self, /, value: int) -> None:
        """
        Set the maximum amount of supported `iceoryx2.Node` instances.
        """
    @property
    def max_notifiers(self, /) -> int:
        """
        The maximum amount of supported `Notifier`
        """
    @max_notifiers.setter
    def max_notifiers(self, /, value: int) -> None:
        """
        Set the maximum amount of supported `Notifier`
        """
    @property
    def notifier_created_event(self, /) -> int:
        """
        Defines the event id value that is emitted after a new notifier was created. If it is
        not set then ``usize::MAX`` is returned
        """
    @notifier_created_event.setter
    def notifier_created_event(self, /, value: int) -> None:
        """
        Sets the event id value that is emitted after a new notifier was created.
        """
    @property
    def notifier_dead_event(self, /) -> int:
        """
        Defines the event id value that is emitted if a notifier was identified as dead.
        """
    @notifier_dead_event.setter
    def notifier_dead_event(self, /, value: int) -> None:
        """
        Sets the event id value that is emitted if a notifier was identified as dead.
        """
    @property
    def notifier_dropped_event(self, /) -> int:
        """
        Defines the event id value that is emitted before a new notifier is dropped.
        """
    @notifier_dropped_event.setter
    def notifier_dropped_event(self, /, value: int) -> None:
        """
        Sets the event id value that is emitted before a new notifier is dropped.
        """

@final
class Global:
    """
    The global settings
    """
    def __str__(self, /) -> str: ...
    @property
    def creation_timeout(self, /) -> Duration:
        """
        Defines the time of how long another process will wait until an entity creation is
        finalized. An entity can be a Service or a Node.
        """
    @creation_timeout.setter
    def creation_timeout(self, /, value: Duration) -> None:
        """
        Set the creation timeout
        """
    @property
    def node(self, /) -> Node:
        """
        Returns the node part of the global configuration
        """
    @property
    def node_dir(self, /) -> Path:
        """
        Returns the directory under which node files are stored.
        """
    @property
    def prefix(self, /) -> FileName:
        """
        Prefix used for all files created during runtime
        """
    @prefix.setter
    def prefix(self, /, value: FileName) -> None:
        """
        Set the prefix used for all files created during runtime
        """
    @property
    def root_path(self, /) -> Path:
        """
        The path under which all other directories or files will be created
        """
    @root_path.setter
    def root_path(self, /, value: Path) -> None:
        """
        Defines the path under which all other directories or files will be created
        """
    @property
    def service(self, /) -> Service:
        """
        Returns the service part of the global configuration
        """
    @property
    def service_dir(self, /) -> Path:
        """
        Returns the directory under which service files are stored.
        """

@final
class Node:
    """
    All configurable settings of a `iceoryx2.Node`.
    """
    def __str__(self, /) -> str: ...
    @property
    def cleanup_dead_nodes_on_creation(self, /) -> bool:
        """
        When true, the `NodeBuilder` checks for dead nodes and
        cleans up all their stale resources whenever a new `iceoryx2.Node` is
        created.
        """
    @cleanup_dead_nodes_on_creation.setter
    def cleanup_dead_nodes_on_creation(self, /, value: bool) -> None:
        """
        Enable/disable the cleanup dead nodes on creation
        """
    @property
    def cleanup_dead_nodes_on_destruction(self, /) -> bool:
        """
        When true, the `NodeBuilder` checks for dead nodes and
        cleans up all their stale resources whenever an existing `iceoryx2.Node` is
        going out of scope.
        """
    @cleanup_dead_nodes_on_destruction.setter
    def cleanup_dead_nodes_on_destruction(self, /, value: bool) -> None:
        """
        Enable/disable the cleanup dead nodes on destruction
        """
    @property
    def directory(self, /) -> Path:
        """
        The directory in which all node files are stored
        """
    @directory.setter
    def directory(self, /, value: Path) -> None:
        """
        Set the directory in which all node files are stored
        """
    @property
    def global_mgmt_suffix(self, /) -> FileName:
        """
        The suffix of the global management segment.
        """
    @global_mgmt_suffix.setter
    def global_mgmt_suffix(self, /, value: FileName) -> None:
        """
        Set the suffix of the files where the node configuration is stored.
        """
    @property
    def monitor_suffix(self, /) -> FileName:
        """
        The suffix of the monitor token
        """
    @monitor_suffix.setter
    def monitor_suffix(self, /, value: FileName) -> None:
        """
        Set the suffix of the monitor token
        """
    @property
    def port_tag_suffix(self, /) -> FileName:
        """
        The suffix of the port tags.
        """
    @port_tag_suffix.setter
    def port_tag_suffix(self, /, value: FileName) -> None:
        """
        Set the suffix of the port tags.
        """
    @property
    def service_tag_suffix(self, /) -> FileName:
        """
        The suffix of the service tags.
        """
    @service_tag_suffix.setter
    def service_tag_suffix(self, /, value: FileName) -> None:
        """
        Set the suffix of the service tags.
        """
    @property
    def static_config_suffix(self, /) -> FileName:
        """
        The suffix of the files where the node configuration is stored.
        """
    @static_config_suffix.setter
    def static_config_suffix(self, /, value: FileName) -> None:
        """
        Set the suffix of the files where the node configuration is stored.
        """

@final
class PublishSubscribe:
    """
    Default settings for the publish-subscribe messaging pattern. These settings are used unless
    the user specifies custom QoS or port settings.
    """
    def __str__(self, /) -> str: ...
    @property
    def backpressure_strategy(self, /) -> BackpressureStrategy:
        """
        If safe overflow is deactivated it defines the deliver strategy of the
        `Publisher` when the `Subscriber`'s buffer is full.
        """
    @backpressure_strategy.setter
    def backpressure_strategy(self, /, value: BackpressureStrategy) -> None:
        """
        Define the backpressure strategy
        """
    @property
    def enable_safe_overflow(self, /) -> bool:
        """
        Defines how the `Subscriber` buffer behaves when it is
        full. When safe overflow is activated, the `Publisher` will
        replace the oldest `Sample` with the newest one.
        """
    @enable_safe_overflow.setter
    def enable_safe_overflow(self, /, value: bool) -> None:
        """
        Enables/disables safe overflow
        """
    @property
    def max_nodes(self, /) -> int:
        """
        The maximum amount of supported `iceoryx2.Node` instances. Defines indirectly how many
        processes can open the service at the same time.
        """
    @max_nodes.setter
    def max_nodes(self, /, value: int) -> None:
        """
        Set the maximum amount of supported `iceoryx2.Node` instances.
        """
    @property
    def max_publishers(self, /) -> int:
        """
        The maximum amount of supported `Publisher` ports
        """
    @max_publishers.setter
    def max_publishers(self, /, value: int) -> None:
        """
        Set the maximum amount of supported `Publisher` ports
        """
    @property
    def max_subscribers(self, /) -> int:
        """
        The maximum amount of supported `Subscriber` ports
        """
    @max_subscribers.setter
    def max_subscribers(self, /, value: int) -> None:
        """
        Set the maximum amount of supported `Subscriber` ports
        """
    @property
    def publisher_history_size(self, /) -> int:
        """
        The maximum history size a `Subscriber` can request from a `Publisher`.
        """
    @publisher_history_size.setter
    def publisher_history_size(self, /, value: int) -> None:
        """
        Set the maximum history size a `Subscriber` can request from a `Publisher`.
        """
    @property
    def publisher_max_loaned_samples(self, /) -> int:
        """
        The maximum `SampleMut` count a `Publisher` can loan at the same time.
        """
    @publisher_max_loaned_samples.setter
    def publisher_max_loaned_samples(self, /, value: int) -> None:
        """
        The maximum `SampleMut` count a `Publisher` can loan at the same time.
        """
    @property
    def subscriber_expired_connection_buffer(self, /) -> int:
        """
        Defines the size of the internal `Subscriber`
        buffer that contains expired connections. An
        connection is expired when the `Publisher`
        disconnected from a service and the connection
        still contains an unconsumed `Sample`.
        """
    @subscriber_expired_connection_buffer.setter
    def subscriber_expired_connection_buffer(self, /, value: int) -> None:
        """
        Set the expired connection buffer size
        """
    @property
    def subscriber_max_borrowed_samples(self, /) -> int:
        """
        The maximum `Sample` count a `Subscriber` can hold at the same time.
        """
    @subscriber_max_borrowed_samples.setter
    def subscriber_max_borrowed_samples(self, /, value: int) -> None:
        """
        Set the maximum `Sample` count a `Subscriber` can hold at the same time.
        """
    @property
    def subscriber_max_buffer_size(self, /) -> int:
        """
        The maximum buffer size a `Subscriber` can have
        """
    @subscriber_max_buffer_size.setter
    def subscriber_max_buffer_size(self, /, value: int) -> None:
        """
        Set the maximum buffer size a `Subscriber` can have
        """

@final
class RequestResponse:
    """
    Default settings for the request response messaging pattern. These settings are used unless
    the user specifies custom QoS or port settings.
    """
    def __str__(self, /) -> str: ...
    @property
    def client_backpressure_strategy(self, /) -> BackpressureStrategy:
        """
        Defines the `BackpressureStrategy` when a `Client`
        could not deliver the request to the `Server`.
        """
    @client_backpressure_strategy.setter
    def client_backpressure_strategy(self, /, value: BackpressureStrategy) -> None:
        """
        Set the `BackpressureStrategy` when a `Client`
        could not deliver the request to the `Server`.
        """
    @property
    def client_expired_connection_buffer(self, /) -> int:
        """
        Defines the size of the internal `Client`
        buffer that contains expired connections. An
        connection is expired when the `Server`
        disconnected from a service and the connection
        still contains an unconsumed `Response`.
        """
    @client_expired_connection_buffer.setter
    def client_expired_connection_buffer(self, /, value: int) -> None:
        """
        Set the size of the internal `Client`
        buffer that contains expired connections. An
        connection is expired when the `Server`
        disconnected from a service and the connection
        still contains an unconsumed `Response`.
        """
    @property
    def enable_fire_and_forget_requests(self, /) -> bool:
        """
        Allows the `Server` to receive a `RequestMut` from a `Client` that is not interested in a
        `Response`, meaning that the `Server` will receive the `RequestMut` despite the
        corresponding `PendingResponse` already went out-of-scope. So any `Response` sent by the
        `Server` would not be received by the corresponding `Client`'s `PendingResponse`.

        Consider enabling this feature if you do not want to loose any `RequestMut`.
        """
    @enable_fire_and_forget_requests.setter
    def enable_fire_and_forget_requests(self, /, value: bool) -> None:
        """
        Set if fire-and-forget feature is enabled
        """
    @property
    def enable_safe_overflow_for_requests(self, /) -> bool:
        """
        Defines if the request buffer of the `iceoryx2.Service` safely overflows.
        """
    @enable_safe_overflow_for_requests.setter
    def enable_safe_overflow_for_requests(self, /, value: bool) -> None:
        """
        Enables/disables safe overflow for the request buffer.
        """
    @property
    def enable_safe_overflow_for_responses(self, /) -> bool:
        """
        Defines if the response buffer of the `iceoryx2.Service` safely overflows.
        """
    @enable_safe_overflow_for_responses.setter
    def enable_safe_overflow_for_responses(self, /, value: bool) -> None:
        """
        Enables/disables safe overflow for the response buffer.
        """
    @property
    def max_active_requests_per_client(self, /) -> int:
        """
        The maximum `ActiveRequest` count a `Server` can hold in
        parallel per `Client`.
        """
    @max_active_requests_per_client.setter
    def max_active_requests_per_client(self, /, value: int) -> None:
        """
        Set the maximum `ActiveRequest` count a `Server` can hold in
        parallel per `Client`.
        """
    @property
    def max_borrowed_responses_per_pending_response(self, /) -> int:
        """
        The maximum amount of borrowed `Response` per
        `PendingResponse` on the `Client` side.
        """
    @max_borrowed_responses_per_pending_response.setter
    def max_borrowed_responses_per_pending_response(self, /, value: int) -> None:
        """
        Set the maximum amount of borrowed `Response` per
        `PendingResponse` on the `Client` side.
        """
    @property
    def max_clients(self, /) -> int:
        """
        The maximum amount of supported `Client`
        """
    @max_clients.setter
    def max_clients(self, /, value: int) -> None:
        """
        Set the maximum amount of supported `Client`
        """
    @property
    def max_loaned_requests(self, /) -> int:
        """
        Defines how many `RequestMut` a
        `Client` can loan in parallel.
        """
    @max_loaned_requests.setter
    def max_loaned_requests(self, /, value: int) -> None:
        """
        Set how many `RequestMut` a
        `Client` can loan in parallel.
        """
    @property
    def max_nodes(self, /) -> int:
        """
        The maximum amount of supported `iceoryx2.Node` instances. Defines
        indirectly how many processes can open the service at the same time.
        """
    @max_nodes.setter
    def max_nodes(self, /, value: int) -> None:
        """
        Set the maximum amount of supported `iceoryx2.Node` instances. Defines
        indirectly how many processes can open the service at the same time.
        """
    @property
    def max_response_buffer_size(self, /) -> int:
        """
        The maximum `Response` buffer size for a
        `PendingResponse`.
        """
    @max_response_buffer_size.setter
    def max_response_buffer_size(self, /, value: int) -> None:
        """
        Set the maximum `Response` buffer size for a
        `PendingResponse`.
        """
    @property
    def max_servers(self, /) -> int:
        """
        The maximum amount of supported `Server`
        """
    @max_servers.setter
    def max_servers(self, /, value: int) -> None:
        """
        Set the maximum amount of supported `Server`
        """
    @property
    def server_backpressure_strategy(self, /) -> BackpressureStrategy:
        """
        Defines the `BackpressureStrategy` when a `Server`
        could not deliver the response to the `Client`.
        """
    @server_backpressure_strategy.setter
    def server_backpressure_strategy(self, /, value: BackpressureStrategy) -> None:
        """
        Set the `BackpressureStrategy` when a `Server`
        could not deliver the response to the `Client`.
        """
    @property
    def server_expired_connection_buffer(self, /) -> int:
        """
        Defines the size of the internal `Server`
        buffer that contains expired connections. An
        connection is expired when the `Client`
        disconnected from a service and the connection
        still contains an unconsumed `ActiveRequest`.
        """
    @server_expired_connection_buffer.setter
    def server_expired_connection_buffer(self, /, value: int) -> None:
        """
        Set the size of the internal `Server`
        buffer that contains expired connections. An
        connection is expired when the `Client`
        disconnected from a service and the connection
        still contains an unconsumed `ActiveRequest`.
        """
    @property
    def server_max_loaned_responses_per_request(self, /) -> int:
        """
        Defines how many `ResponseMut` a `Server` can loan in
        parallel per `ActiveRequest`.
        """
    @server_max_loaned_responses_per_request.setter
    def server_max_loaned_responses_per_request(self, /, value: int) -> None:
        """
        Set how many `ResponseMut` a `Server` can loan in
        parallel per `ActiveRequest`.
        """

@final
class Service:
    """
    All configurable settings of a `iceoryx2.Service`.
    """
    def __str__(self, /) -> str: ...
    @property
    def cleanup_dead_nodes_on_open(self, /) -> bool:
        """
        When true, the `ServiceBuilder` will clean up dead nodes when opening an
        existing service.
        """
    @cleanup_dead_nodes_on_open.setter
    def cleanup_dead_nodes_on_open(self, /, value: bool) -> None:
        """
        Sets if dead nodes shall be cleaned up whenever the `ServiceBuilder` opens
        an existing service.
        """
    @property
    def connection_suffix(self, /) -> FileName:
        """
        The suffix of a one-to-one connection
        """
    @connection_suffix.setter
    def connection_suffix(self, /, value: FileName) -> None:
        """
        Set the suffix of a one-to-one connection
        """
    @property
    def data_segment_suffix(self, /) -> FileName:
        """
        The suffix of the ports data segment
        """
    @data_segment_suffix.setter
    def data_segment_suffix(self, /, value: FileName) -> None:
        """
        Set the suffix of the ports data segment
        """
    @property
    def directory(self, /) -> Path:
        """
        The directory in which all service files are stored
        """
    @directory.setter
    def directory(self, /, value: Path) -> None:
        """
        Set the directory in which all service files are stored
        """
    @property
    def dynamic_config_storage_suffix(self, /) -> FileName:
        """
        The suffix of the dynamic config file
        """
    @dynamic_config_storage_suffix.setter
    def dynamic_config_storage_suffix(self, /, value: FileName) -> None:
        """
        Set the suffix of the dynamic config file
        """
    @property
    def event_connection_suffix(self, /) -> FileName:
        """
        The suffix of a one-to-one connection
        """
    @event_connection_suffix.setter
    def event_connection_suffix(self, /, value: FileName) -> None:
        """
        Set the suffix of a one-to-one connection
        """
    @property
    def flatbuffer_schema_path(self, /) -> Path | None:
        """
        A list of directories where iceoryx2 will look for ``.fbs`` flatbuffer schemas. If no path
        is provided, iceoryx2 will perform no lookup and the user must explicitly define the path to
        the flatbuffer schemas.
        """
    @flatbuffer_schema_path.setter
    def flatbuffer_schema_path(self, /, value: Path | None) -> None:
        """
        Set the directory which will be used to lookup flatbuffer schema files.
        """
    @property
    def static_config_storage_suffix(self, /) -> FileName:
        """
        The suffix of the static config file
        """
    @static_config_storage_suffix.setter
    def static_config_storage_suffix(self, /, value: FileName) -> None:
        """
        Set the suffix of the static config file
        """

def default() -> Config: ...

def default_config_file_name() -> FileName:
    """
    The name of the default iceoryx2 config file
    """

def default_config_file_path() -> FilePath:
    """
    Path to the default config file
    """

def default_user_config_file_path() -> FilePath:
    """
    Path to the default user config file
    """

def from_file(config_file: FilePath) -> Config:
    """
    Loads a configuration from a file. On success it returns a `Config` object otherwise a
    `ConfigCreationError` describing the failure.
    """

def from_toml(content: str) -> Config: ...
def global_config() -> Config: ...
def into_toml(config: Config) -> str: ...

def relative_config_path() -> Path:
    """
    Relative path to the config file
    """

def setup_global_config_from_file(config_file: FilePath) -> Config: ...
