"""
iceoryx2 Python language bindings
"""

from . import config as config, testing as testing
from .config import Config
from _typeshed import Incomplete
from iceoryx2 import ActiveRequest as ActiveRequest2, Client as Client2, EntryHandle as EntryHandle2, EntryHandleMut as EntryHandleMut2, EntryValueUninit as EntryValueUninit2, PendingResponse as PendingResponse2, PortFactoryBlackboard as PortFactoryBlackboard2, PortFactoryClient as PortFactoryClient2, PortFactoryPublisher as PortFactoryPublisher2, PortFactoryServer as PortFactoryServer2, Publisher as Publisher2, Reader as Reader2, RequestMut as RequestMut2, RequestMutUninit as RequestMutUninit2, Response as Response2, ResponseMut as ResponseMut2, ResponseMutUninit as ResponseMutUninit2, Sample as Sample2, SampleMut as SampleMut2, SampleMutUninit as SampleMutUninit2, ServiceBuilder as ServiceBuilder2, ServiceBuilderBlackboardCreator as ServiceBuilderBlackboardCreator2, ServiceBuilderPublishSubscribe as ServiceBuilderPublishSubscribe2, ServiceBuilderRequestResponse as ServiceBuilderRequestResponse2, Writer as Writer2
from typing import Any, Final, final

@final
class ActiveRequest:
    """
    The `ActiveRequest` represents the object that contains the payload that the `Client` sends to the
    `Server`.
    """
    def __loan_slice_uninit(self, /, slice_len: int) -> ResponseMutUninit2:
        """
        Loans/allocates a `ResponseMutUninit` from the underlying data segment of the
        `Server`. The user has to initialize the payload before it can be sent.

        On failure it emits `LoanError` describing the failure.
        """
    def __loan_uninit(self, /) -> ResponseMutUninit2:
        """
        Loans uninitialized memory for a `ResponseMut` where the user can write its payload to.
        """
    @property
    def __request_header_type_details(self, /) -> Any | None: ...
    @property
    def __request_payload_type_details(self, /) -> Any | None: ...
    @property
    def __response_header_type_details(self, /) -> Any | None: ...
    @property
    def __response_payload_type_details(self, /) -> Any | None: ...
    @property
    def __slice_len(self, /) -> int: ...
    def delete(self, /) -> None:
        """
        Releases the `ActiveRequest` and terminates the connection.

        After this call the `ActiveRequest` is no longer usable!
        """
    @property
    def has_disconnect_hint(self, /) -> bool:
        """
        Returns `True` if the `Client` wants to gracefully disconnect.
        This allows the `Server` to send its last response and then
        drop the `ActiveRequest` to signal the `Client` that no more
        `ResponseMut` will be sent.
        """
    @property
    def header(self, /) -> RequestHeader:
        """
        Returns the `RequestHeader` of the received `RequestMut`
        """
    @property
    def is_connected(self, /) -> bool:
        """
        Returns `True` until the `PendingResponse` goes out of scope on the `Client`'s side
        indicating that the `Client` no longer receives the `ResponseMut`.
        """
    @property
    def origin(self, /) -> UniqueClientId:
        """
        Returns the `UniqueClientId` of the `Client`
        """
    @property
    def payload_ptr(self, /) -> int:
        """
        Returns the address of the payload of the received `RequestMut` as an `int`.
        `ActiveRequest.payload` provides typed access.
        """
    @property
    def user_header_ptr(self, /) -> int:
        """
        Returns the address of the user_header of the received `RequestMut` as an `int`.
        `ActiveRequest.user_header` provides typed access.
        """

@final
class Alignment:
    """
    Contains the alignment memory can have.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @staticmethod
    def new(value: int) -> Alignment:
        """
        Creates a new `Alignment`. If the value is zero or not a power of 2
        it emits an `InvalidAlignmentValue`.
        """
    def value(self, /) -> int:
        """
        Returns the value of the `Alignment`
        """

@final
class AliveNodeView:
    """
    Contains all details of a `Node` that is alive.
    """
    @property
    def details(self, /) -> NodeDetails | None:
        """
        Returns optional `NodeDetails` that contains further information about the `Node`.
        Can only be acquired when the process has the access right to read it.
        """
    @property
    def id(self, /) -> UniqueNodeId:
        """
        Returns the `UniqueNodeId`.
        """

@final
class AllocationStrategy:
    """
    Describes generically an `AllocationStrategy`, meaning how the memory is increased when the
    available memory is insufficient.
    """
    BestFit: Final[AllocationStrategy]
    """
    Increases the memory so that it perfectly fits the new size requirements. This may lead
    to a lot of reallocations but has the benefit that no byte is wasted.
    """
    PowerOfTwo: Final[AllocationStrategy]
    """
    Increases the memory by rounding the increased memory size up to the next power of two.
    Reduces reallocations a lot at the cost of increased memory usage.
    """
    Static: Final[AllocationStrategy]
    """
    The memory is not increased. This may lead to an out-of-memory error when allocating.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __int__(self, /) -> int: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __repr__(self, /) -> str: ...
    def __str__(self, /) -> str: ...

@final
class Attribute:
    """
    Represents a single service attribute (key-value) pair that can be defined when the service
    is being created.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @property
    def key(self, /) -> AttributeKey:
        """
        Acquires the service attribute key
        """
    @staticmethod
    def new(key: AttributeKey, value: AttributeValue) -> Attribute:
        """
        Creates an attribute instance
        """
    @property
    def value(self, /) -> AttributeValue:
        """
        Acquires the service attribute value
        """

@final
class AttributeKey:
    """
    Relocatable (inter-process shared memory compatible) ``SemanticString`` implementation for
    `AttributeKey`.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @staticmethod
    def max_len() -> int:
        """
        Returns the maximum length of a `AttributeKey`
        """
    @staticmethod
    def new(value: str) -> AttributeKey:
        """
        Creates a new `AttributeKey` when the provided ``value`` does not exceed
        `AttributeKey.max_len()`, otherwise it emits a `SemanticStringError`.
        """
    def to_string(self, /) -> str:
        """
        Converts the `AttributeKey` into a `str`
        """

@final
class AttributeSet:
    """
    Represents a single service attribute (key-value) pair that can be defined when the service
    is being created.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @staticmethod
    def capacity() -> int:
        """
        Returns the maximum `Attribute` count the `AttributeSet` can hold.
        """
    def key_values(self, /, key: AttributeKey) -> list[AttributeValue]:
        """
        Returns all `AttributeValue` that belong to a specified `AttributeKey`.
        """
    @property
    def number_of_attributes(self, /) -> int:
        """
        Returns the `Attribute` count of the `AttributeSet`.
        """
    @property
    def values(self, /) -> list[Attribute]:
        """
        Returns every `Attribute` stored in the `AttributeSet`
        """

@final
class AttributeSpecifier:
    """
    Represents a single service attribute (key-value) pair that can be defined when the service
    is being created.
    """
    def __str__(self, /) -> str: ...
    @property
    def attributes(self, /) -> AttributeSet:
        """
        Returns the underlying `AttributeSet`
        """
    def define(self, /, key: AttributeKey, value: AttributeValue) -> AttributeSpecifier:
        """
        Defines a value for a specific key. A key is allowed to have multiple values.
        """
    @staticmethod
    def new() -> AttributeSpecifier:
        """
        Creates a new empty `Attribute` set
        """

@final
class AttributeValue:
    """
    Relocatable (inter-process shared memory compatible) ``SemanticString`` implementation for
    `AttributeValue`.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @staticmethod
    def max_len() -> int:
        """
        Returns the maximum length of a `AttributeValue`
        """
    @staticmethod
    def new(value: str) -> AttributeValue:
        """
        Creates a new `AttributeValue` when the provided ``value`` does not exceed
        `AttributeValue.max_len()`, otherwise it emits a `SemanticStringError`.
        """
    def to_string(self, /) -> str:
        """
        Converts the `AttributeValue` into a `str`
        """

@final
class AttributeVerifier:
    """
    Represents a single service attribute (key-value) pair that can be defined when the service
    is being created.
    """
    def __str__(self, /) -> str: ...
    @staticmethod
    def new() -> AttributeVerifier:
        """
        Creates a new empty `Attribute` set
        """
    def require(self, /, key: AttributeKey, value: AttributeValue) -> AttributeVerifier:
        """
        Requires a value for a specific key. A key is allowed to have multiple values.
        """
    def require_key(self, /, key: AttributeKey) -> AttributeVerifier:
        """
        Requires that a specific key is defined.
        """
    @property
    def required_attributes(self, /) -> AttributeSet:
        """
        Returns the underlying required `AttributeSet`
        """
    @property
    def required_keys(self, /) -> list[AttributeKey]:
        """
        Returns the underlying required keys
        """
    def verify_requirements(self, /, rhs: AttributeSet) -> AttributeKey | None:
        """
        Verifies if the `AttributeSet` contains all required keys and key-value pairs.
        """

@final
class BackpressureStrategy:
    """
    Defines the strategy a sender shall pursue when the buffer of the receiver is full
    and the service does not overflow.
    """
    DiscardData: Final[BackpressureStrategy]
    """
    Do not deliver the data to receiver with a full buffer
    """
    RetryUntilDelivered: Final[BackpressureStrategy]
    """
    Retries until the receiver has consumed some
    data from the full buffer and there is space again
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __int__(self, /) -> int: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __repr__(self, /) -> str: ...
    def __str__(self, /) -> str: ...

@final
class Client:
    """
    Represents the receiving endpoint of an event based communication.
    """
    def __loan_slice_uninit(self, /, slice_len: int) -> RequestMutUninit2:
        """
        Loans/allocates a `RequestMutUninit` from the underlying data segment of the `Client`.
        The user has to initialize the payload before it can be sent.

        On failure it emits a `LoanError` describing the failure.
        """
    def __loan_uninit(self, /) -> RequestMutUninit2:
        """
        Acquires an `RequestMutUninit` to store payload. This API shall be used
        by default to avoid unnecessary copies.
        """
    @property
    def __request_header_type_details(self, /) -> Any | None: ...
    @property
    def __request_payload_type_details(self, /) -> Any | None: ...
    @property
    def __response_header_type_details(self, /) -> Any | None: ...
    @property
    def __response_payload_type_details(self, /) -> Any | None: ...
    @property
    def backpressure_strategy(self, /) -> BackpressureStrategy:
        """
        Returns the strategy the `Client` follows when a `RequestMut` cannot be delivered
        if the `Server`'s buffer is full.
        """
    def delete(self, /) -> None:
        """
        Releases the `Client`.

        After this call the `Client` is no longer usable!
        """
    @property
    def id(self, /) -> UniqueClientId:
        """
        Returns the `UniqueClientId` of the `Client`
        """
    def initial_max_slice_len(self, /) -> int:
        """
        Returns the maximum initial slice length configured for this `Client`.
        """
    @property
    def max_active_requests(self, /) -> int:
        """
        Returns the maximum amount of active requests the `Client` can send.
        """
    @property
    def name(self, /) -> PortName:
        """
        Returns the `PortName` of the `Client`
        """

@final
class DeadNodeView:
    """
    Contains all details of a `Node` that is dead.
    """
    def blocking_remove_stale_resources(self, /, timeout: Duration) -> None:
        """
        Removes all stale resources of a dead `Node`. If another instance
        is already removing the dead `Node` it waits until the other instance
        has cleaned up the dead `Node` completely. If the other cleanup instance
        crashes, it will take over the ownership and continue the cleanup.
        If the process does not have the permission to cleanup all resources it
        aborts with an error.

        If the provided timeout is expired it will return.
        """
    @property
    def details(self, /) -> NodeDetails | None:
        """
        Returns optional `NodeDetails` that contains further information about the `Node`.
        Can only be acquired when the process has the access right to read it.
        """
    @property
    def id(self, /) -> UniqueNodeId:
        """
        Returns the `UniqueNodeId`.
        """
    def try_remove_stale_resources(self, /) -> None:
        """
        Removes all stale resources of the dead `Node`. On error it emits a `NodeCleanupFailure`.
        It returns true if the stale resources could be removed, otherwise false.
        """

@final
class Duration:
    """
    Represents a time duration.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    def as_micros(self, /) -> int:
        """
        Returns the number of micro seconds stored in the `Duration`
        """
    def as_millis(self, /) -> int:
        """
        Returns the number of milli seconds stored in the `Duration`
        """
    def as_nanos(self, /) -> int:
        """
        Returns the number of nano seconds stored in the `Duration`
        """
    def as_secs(self, /) -> int:
        """
        Returns the number of seconds stored in the `Duration`
        """
    def as_secs_f64(self, /) -> float:
        """
        Returns the number of seconds stored in the `Duration`
        """
    @staticmethod
    def from_micros(micros: int) -> Duration:
        """
        Creates a new `Duration` from a given number of micro seconds
        """
    @staticmethod
    def from_millis(millis: int) -> Duration:
        """
        Creates a new `Duration` from a given number of milli seconds
        """
    @staticmethod
    def from_nanos(nanos: int) -> Duration:
        """
        Creates a new `Duration` from a given number of nano seconds
        """
    @staticmethod
    def from_secs(secs: int) -> Duration:
        """
        Creates a new `Duration` from a given number of seconds
        """
    @staticmethod
    def from_secs_f64(secs: float) -> Duration:
        """
        Creates a new `Duration` from a given number of seconds
        """
    def subsec_micros(self, /) -> int:
        """
        Returns the fractional micro seconds part stored in the `Duration`
        """
    def subsec_millis(self, /) -> int:
        """
        Returns the fractional milli seconds part stored in the `Duration`
        """
    def subsec_nanos(self, /) -> int:
        """
        Returns the fractional nano seconds part stored in the `Duration`
        """

@final
class DynamicConfigBlackboard:
    """
    The dynamic configuration of a `MessagingPattern.Blackboard` service.
    Port counts reflect the current state of the service when accessed.
    The view keeps the service open while it is referenced.
    Explicitly deleting the blackboard factory invalidates the view; subsequent
    count queries raise `RuntimeError`.
    """
    @property
    def number_of_readers(self, /) -> int:
        """
        Returns the number of readers currently connected to the service.
        """
    @property
    def number_of_writers(self, /) -> int:
        """
        Returns the number of writers currently connected to the service.
        """

@final
class DynamicConfigEvent:
    """
    The dynamic configuration of a `MessagingPattern.Event` service.
    Port counts reflect the current state of the service when accessed.
    The view keeps the service open while it is referenced.
    """
    @property
    def number_of_listeners(self, /) -> int:
        """
        Returns the number of listeners currently connected to the service.
        """
    @property
    def number_of_notifiers(self, /) -> int:
        """
        Returns the number of notifiers currently connected to the service.
        """

@final
class DynamicConfigPublishSubscribe:
    """
    The dynamic configuration of a `MessagingPattern.PublishSubscribe` service.
    Port counts reflect the current state of the service when accessed.
    The view keeps the service open while it is referenced.
    """
    @property
    def number_of_publishers(self, /) -> int:
        """
        Returns the number of publishers currently connected to the service.
        """
    @property
    def number_of_subscribers(self, /) -> int:
        """
        Returns the number of subscribers currently connected to the service.
        """

@final
class DynamicConfigRequestResponse:
    """
    The dynamic configuration of a `MessagingPattern.RequestResponse` service.
    Port counts reflect the current state of the service when accessed.
    The view keeps the service open while it is referenced.
    """
    @property
    def number_of_clients(self, /) -> int:
        """
        Returns the number of clients currently connected to the service.
        """
    @property
    def number_of_servers(self, /) -> int:
        """
        Returns the number of servers currently connected to the service.
        """

@final
class EntryHandle:
    def __get(self, /) -> tuple[int, int]: ...
    def __is_up_to_date(self, /, generation_counter: int) -> bool: ...
    def __set_value_ptr(self, /) -> None: ...
    def __set_value_type(self, /, value: Any) -> None: ...
    @property
    def __value_type(self, /) -> Any | None: ...
    @property
    def entry_id(self, /) -> EventId:
        """
        Returns an ID corresponding to the entry which can be used in an event based communication
        setup.
        """

@final
class EntryHandleMut:
    def __get_data_ptr(self, /, value_size: int, value_alignment: int) -> int: ...
    def __set_value_type(self, /, value: Any) -> None: ...
    def __update_data_ptr(self, /) -> None: ...
    @property
    def __value_type(self, /) -> Any | None: ...
    def delete(self, /) -> None:
        """
        Releases the `EntryHandleMut`.

        After this call the `EntryHandleMut` is no longer usable!
        """
    @property
    def entry_id(self, /) -> EventId:
        """
        Returns an ID corresponding to the entry which can be used in an event based
        communication setup.
        """
    def loan_uninit(self, /) -> EntryValueUninit2:
        """
        Consumes the `EntryHandleMut` and loans an uninitialized entry value that can be used to
        update without copy.
        """

@final
class EntryValueUninit:
    def __get_write_cell(self, /) -> int: ...
    def __update_write_cell(self, /) -> EntryHandleMut2: ...
    @property
    def __value_type(self, /) -> Any | None: ...
    def discard(self, /) -> EntryHandleMut2:
        """
        Discards the `EntryValueUninit` and returns the original
        `EntryHandleMut`.
        """

@final
class EventActivation:
    """
    User defined identifier that can be provided in `Notifier.notify()` to signal a specific
    kind of event.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @property
    def count(self, /) -> int:
        """
        Returns how often the `EventId` was notified
        """
    @property
    def id(self, /) -> EventId:
        """
        Returns the `EventId`
        """

@final
class EventId:
    """
    User defined identifier that can be provided in `Notifier.notify()` to signal a specific
    kind of event.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @property
    def as_value(self, /) -> int:
        """
        Returns the integer value of the `EventId`
        """
    @staticmethod
    def new(value: int) -> EventId:
        """
        Creates a new `EventId` from a given integer value
        """

@final
class FileDescriptor:
    """
    Represents a FileDescriptor in a POSIX system. Contains always a value greater or equal zero,
    a valid file descriptor. It takes the ownership of the provided file descriptor and calls
    ``posix::close`` on destruction.
    """
    def __str__(self, /) -> str: ...
    @property
    def native_handle(self, /) -> int:
        """
        Returns the underlying value of the FileDescriptor

        # Safety

         * the user shall not store the value in a variable otherwise lifetime issues may be
           encountered
         * do not manually close the file descriptor with a sys call
        """
    @staticmethod
    def new(value: int) -> FileDescriptor | None:
        """
        Creates a new FileDescriptor. If the value is smaller than zero it returns `None`.
        """
    @staticmethod
    def non_owning_new(value: int) -> FileDescriptor | None:
        """
        Creates a FileDescriptor which does not hold the ownership of the file descriptor and will
        not call ``posix::close`` on destruction.
        """

@final
class FileName:
    """
    Relocatable (inter-process shared memory compatible) ``SemanticString`` implementation for
    `FileName`. All modification operations ensure that never an
    invalid file or path name can be generated. All strings have a fixed size so that the maximum
    path or file name length the system supports can be stored.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @staticmethod
    def max_len() -> int:
        """
        Returns the maximum length of a `FileName`
        """
    @staticmethod
    def new(name: str) -> FileName:
        """
        Creates a new `FileName` when the provided ``name`` contains a valid path to a file,
        otherwise it emits a `SemanticStringError`.
        """
    def to_string(self, /) -> str:
        """
        Converts the `FileName` into a `str`
        """

@final
class FilePath:
    """
    Relocatable (inter-process shared memory compatible) ``SemanticString`` implementation for
    `FilePath`. All modification operations ensure that never an
    invalid file or path name can be generated. All strings have a fixed size so that the maximum
    path or file name length the system supports can be stored.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @staticmethod
    def max_len() -> int:
        """
        Returns the maximum length of a `FilePath`
        """
    @staticmethod
    def new(name: str) -> FilePath:
        """
        Creates a new `FilePath` when the provided ``name`` contains a valid path to a file,
        otherwise it emits a `SemanticStringError`.
        """
    def to_string(self, /) -> str:
        """
        Converts the `FilePath` into a `str`
        """

@final
class HeaderPublishSubscribe:
    """
    Sample header used by `MessagingPattern.PublishSubscribe`
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    @property
    def node_id(self, /) -> UniqueNodeId:
        """
        Returns the `UniqueNodeId` of the source node that published the `Sample`.
        """
    @property
    def number_of_elements(self, /) -> int:
        """
        Returns how many elements are stored inside the `Sample`'s payload.
        """
    @property
    def payload_offset(self, /) -> int:
        """
        Returns the payload offset.
        """
    @property
    def publisher_id(self, /) -> UniquePublisherId:
        """
        Returns the `UniquePublisherId` of the source `Publisher`.
        """

@final
class Listener:
    """
    Represents the receiving endpoint of an event based communication.
    """
    def blocking_wait(self, /) -> list[EventActivation]:
        """
        Blocking wait for new events. Unblocks as soon
        as an event was received and then collects every `EventActivation` that was received
        and returns them.
        On error it emits `ListenerWaitError`.
        """
    @property
    def deadline(self, /) -> Duration | None:
        """
        Returns the deadline of the corresponding `Service`.
        """
    def delete(self, /) -> None:
        """
        Releases the `Listener`.

        After this call the `Listener` is no longer usable!
        """
    @property
    def id(self, /) -> UniqueListenerId:
        """
        Returns the `UniqueListenerId` of the `Listener`
        """
    @property
    def name(self, /) -> PortName:
        """
        Returns the `PortName` of the `Listener`
        """
    def timed_wait(self, /, timeout: Duration) -> list[EventActivation]:
        """
        Blocking wait for new events until the provided timeout has passed. Unblocks as soon
        as an event was received and then collects every `EventActivation` that was received
        and returns them.
        On error it emits `ListenerWaitError`.
        """
    def try_wait(self, /) -> list[EventActivation]:
        """
        Non-blocking wait for new events. Collects every `EventActivation` that was received
        and returns them.
        On error it emits `ListenerWaitError`.
        """

@final
class LogLevel:
    """
    Describes the log level.
    """
    Debug: Final[LogLevel]
    Error: Final[LogLevel]
    Fatal: Final[LogLevel]
    Info: Final[LogLevel]
    Trace: Final[LogLevel]
    Warn: Final[LogLevel]
    def __eq__(self, /, other: object) -> bool: ...
    def __int__(self, /) -> int: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __repr__(self, /) -> str: ...
    def __str__(self, /) -> str: ...

@final
class MessageTypeDetails:
    """
    Contains all type information to the header and payload type.
    """
    @property
    def header(self, /) -> TypeDetail:
        """
        The `TypeDetail` of the header of a message, the first iceoryx2 internal part.
        """
    @property
    def payload(self, /) -> TypeDetail:
        """
        The `TypeDetail` of the payload of the message, the last part.
        """
    @property
    def user_header(self, /) -> TypeDetail:
        """
        The `TypeDetail` of the user_header or the custom header, is located directly after the
        header.
        """

@final
class MessagingPattern:
    Blackboard: Final[MessagingPattern]
    Event: Final[MessagingPattern]
    PublishSubscribe: Final[MessagingPattern]
    RequestResponse: Final[MessagingPattern]
    def __eq__(self, /, other: object) -> bool: ...
    def __int__(self, /) -> int: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __repr__(self, /) -> str: ...
    def __str__(self, /) -> str: ...

@final
class Node:
    """
    The central entry point of iceoryx2. Represents a node of the iceoryx2
    system. One process can have arbitrary many nodes but usually it should be
    only one node per process.
    Can be created via the `NodeBuilder`.
    """
    def __str__(self, /) -> str: ...
    def blocking_cleanup_dead_nodes(self, /, timeout: Duration) -> Any:
        """
        Removes the stale system resources of every dead `Node`. A dead `Node` is also
        removed from every registered `Service`.

        If a `Node` cannot be cleaned up since the process has insufficient permissions then the
        `Node` is skipped. If it is currently being cleaned up by another process then the
        cleaner will wait until the timeout as either passed or the cleaned was finished.

        The timeout is applied to every individual dead `Node` the function needs to wait on.
        """
    @property
    def config(self, /) -> Config:
        """
        Returns the `config.Config` that the `Node` will use to create any iceoryx2 entity.
        """
    def force_remove_service(self, /, name: ServiceName, messaging_pattern: MessagingPattern) -> bool:
        """
        Removes a `Service` by force. This shall be used if the
        resources could not be removed in a previous run and now it is no longer possible to
        open the service.

        # Safety

        No other process shall continue to use the service.
        """
    @property
    def id(self, /) -> UniqueNodeId:
        """
        Returns the unique id of the `Node`.
        """
    @staticmethod
    def list(service_type: ServiceType, config: Config) -> list[NodeState]:
        """
        Returns the `NodeState` of every `Node` under a provided config.
        On failure it emits a `NodeListFailure`.
        """
    @property
    def name(self, /) -> NodeName:
        """
        Returns the name of the node inside a `NodeName`.
        """
    def service_builder(self, /, name: ServiceName) -> ServiceBuilder2:
        """
        Instantiates a `ServiceBuilder` for a service with the provided name.
        """
    @property
    def signal_handling_mode(self, /) -> SignalHandlingMode:
        """
        Returns the `SignalHandlingMode` with which the `Node` was created.
        """
    def try_cleanup_dead_nodes(self, /) -> Any:
        """
        Removes the stale system resources of every dead `Node`. A dead `Node` is also
        removed from every registered `Service`.

        If a `Node` cannot be cleaned up since the process has insufficient permissions then
        the `Node` is skipped.
        """
    def wait(self, /, cycle_time: Duration) -> None:
        """
        Waits for a given ``cycle_time``.
        On failure it emits a `NodeWaitFailure`.
        """
    def waitset_builder(self, /) -> WaitSetBuilder:
        """
        Instantiates a `WaitSetBuilder`
        """

@final
class NodeBuilder:
    """
    Creates a new `Node`.
    """
    def __str__(self, /) -> str: ...
    def config(self, /, config: Config) -> NodeBuilder:
        """
        The `config.Config` that shall be used for the `Node`. If no `config.Config`
        is specified the `config.global_config` is used.
        """
    def create(self, /, service_type: ServiceType) -> Node:
        """
        Creates a new `Node` for a specified `ServiceType`.
        Emits `NodeCreationFailure` on failure.
        """
    def name(self, /, value: NodeName) -> NodeBuilder:
        """
        The `NodeName` that shall be assigned to the `Node`. It does not
        have to be unique. If no `NodeName` is defined then the `Node`
        does not have a name.
        """
    @staticmethod
    def new() -> NodeBuilder:
        """
        Instantiates a new `NodeBuilder`
        """
    def signal_handling_mode(self, /, value: SignalHandlingMode) -> NodeBuilder:
        """
        Defines the `SignalHandlingMode` for the `Node`. It affects the `Node.wait()` call
        that returns any received signal via its `NodeWaitFailure`
        """

@final
class NodeDetails:
    """
    Contains details of a `Node`.
    """
    @property
    def config(self, /) -> Config:
        """
        Returns a reference to the `config.Config` the `Node` uses.
        """
    @property
    def executable(self, /) -> FileName:
        """
        Returns the executable `FileName` of the `Node`'s owner process.
        """
    @property
    def name(self, /) -> NodeName:
        """
        Returns a reference of the `NodeName`.
        """
    @property
    def process_id(self, /) -> int:
        """
        Returns the process id of the `Node`'s owner process.
        """

@final
class NodeName:
    """
    Represent the name for a `Node`.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    def as_str(self, /) -> str:
        """
        Converts the `NodeName` into a `str`
        """
    @staticmethod
    def max_len() -> int:
        """
        Returns the maximum length of a `NodeName`
        """
    @staticmethod
    def new(name: str) -> NodeName:
        """
        Creates a new `NodeName`.
        If the provided name does not contain a valid `NodeName` it will emit
        `SemanticStringError`, otherwise the `NodeName`.
        """

class NodeState:
    """
    Describes the state of a `Node`.
    """
    @final
    class Alive(NodeState):
        """
        The `Node`'s process is still alive.
        """
        __match_args__: Final = ("_0",)
        @property
        def _0(self, /) -> AliveNodeView: ...
        def __getitem__(self, /, key: int) -> Any: ...
        def __len__(self, /) -> int: ...
        def __new__(cls, /, _0: AliveNodeView) -> NodeState.Alive: ...
    @final
    class Dead(NodeState):
        """
        The `Node`'s process died without cleaning up the `Node`'s resources. Another process has
        now the responsibility to cleanup all the stale resources.
        """
        __match_args__: Final = ("_0",)
        @property
        def _0(self, /) -> DeadNodeView: ...
        def __getitem__(self, /, key: int) -> Any: ...
        def __len__(self, /) -> int: ...
        def __new__(cls, /, _0: DeadNodeView) -> NodeState.Dead: ...
    @final
    class Inaccessible(NodeState):
        """
        The process does not have sufficient permissions to identify the `Node` as dead or alive.
        """
        __match_args__: Final = ("_0",)
        @property
        def _0(self, /) -> UniqueNodeId: ...
        def __getitem__(self, /, key: int) -> Any: ...
        def __len__(self, /) -> int: ...
        def __new__(cls, /, _0: UniqueNodeId) -> NodeState.Inaccessible: ...
    @final
    class Undefined(NodeState):
        """
        The `Node` is in an undefined state, meaning that certain elements are missing,
        misconfigured or inconsistent. This can only happen due to an implementation failure or
        when the corresponding `Node` resources were altered.
        """
        __match_args__: Final = ("_0",)
        @property
        def _0(self, /) -> UniqueNodeId: ...
        def __getitem__(self, /, key: int) -> Any: ...
        def __len__(self, /) -> int: ...
        def __new__(cls, /, _0: UniqueNodeId) -> NodeState.Undefined: ...

@final
class Notifier:
    """
    Represents the sending endpoint of an event based communication.
    """
    @property
    def deadline(self, /) -> Duration | None:
        """
        Returns the deadline of the corresponding `Service`.
        """
    def delete(self, /) -> None:
        """
        Releases the `Notifier`.

        After this call the `Notifier` is no longer usable!
        """
    @property
    def id(self, /) -> UniqueNotifierId:
        """
        Returns the `UniqueNotifierId` of the `Notifier`
        """
    @property
    def name(self, /) -> PortName:
        """
        Returns the `PortName` of the `Notifier`
        """
    def notify(self, /) -> int:
        """
        Notifies all `Listener` connected to the service with the default
        event id provided on creation.
        Returns on success the number of `Listener` ports that were notified otherwise it emits
        `NotifierNotifyError`.
        """
    def notify_with_custom_event_id(self, /, event_id: EventId) -> int:
        """
        Notifies all `Listener` connected to the service with a custom `EventId`.
        Returns on success the number of `Listener` ports that were notified otherwise it returns
        `NotifierNotifyError`.
        """

@final
class Path:
    """
    Relocatable (inter-process shared memory compatible) SemanticString implementation for
    `Path`. All modification operations ensure that never an
    invalid file or path name can be generated. All strings have a fixed size so that the maximum
    path or file name length the system supports can be stored.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @staticmethod
    def max_len() -> int:
        """
        Returns the maximum length of a `Path`
        """
    @staticmethod
    def new(name: str) -> Path:
        """
        Creates a new `Path` when the provided ``name`` contains a valid path, otherwise it emits a
        `SemanticStringError`.
        """
    def to_string(self, /) -> str:
        """
        Converts the `Path` into a `str`
        """

@final
class PendingResponse:
    """
    Represents an active connection to all `Server` that received the `RequestMut`. The
    `Client` can use it to receive every corresponding `Response`.

    As soon as it goes out of scope, the connections are closed and every `Server` is informed.
    """
    @property
    def __request_header_type_details(self, /) -> Any | None: ...
    @property
    def __request_payload_type_details(self, /) -> Any | None: ...
    @property
    def __response_header_type_details(self, /) -> Any | None: ...
    @property
    def __response_payload_type_details(self, /) -> Any | None: ...
    def delete(self, /) -> None:
        """
        Releases the `PendingResponse` and signals the `Server` that the `Client` is no longer
        interested in receiving another `Response` and terminates the connection.

        After this call the `PendingResponse` is no longer usable!
        """
    @property
    def has_response(self, /) -> bool:
        """
        Returns `True` when a `Server` has sent a `Response` otherwise `False`.
        """
    @property
    def header(self, /) -> RequestHeader:
        """
        Returns a reference to the iceoryx2 internal `RequestHeader` of the corresponding
        `RequestMut`
        """
    @property
    def is_connected(self, /) -> bool:
        """
        Returns `True` until the `ActiveRequest` goes out of scope on the `Server`'s side
        indicating that the `Server` will no longer send a `Response`.
        It also returns `False` when there are no `Server`.
        """
    @property
    def number_of_server_connections(self, /) -> int:
        """
        Returns how many `Server` ports received the corresponding `RequestMut` initially.
        """
    @property
    def payload_ptr(self, /) -> int:
        """
        Returns the address of the request payload of the corresponding
        `RequestMut` as an `int`.
        `PendingResponse.payload` provides typed access.
        """
    def receive(self, /) -> Response2 | None:
        """
        Receives a `Response` from a `Server` that received the `RequestMut`.
        """
    def set_disconnect_hint(self, /) -> None:
        """
        Marks the connection state that the `Client` wants to gracefully
        disconnect. When the `Server` reads this, it can send the last `Response` and drop the
        corresponding `ActiveRequest` to terminate the
        connection ensuring that no `Response` is lost on the `Client`
        side.
        """
    @property
    def user_header_ptr(self, /) -> int:
        """
        Returns the address of the user defined request header of the corresponding
        `RequestMut` as an `int`.
        `PendingResponse.user_header` provides typed access.
        """

@final
class PortFactoryBlackboard:
    """
    The factory for `MessagingPattern.Blackboard`. It can acquire dynamic and static service
    information and create `Reader` or `Writer` ports.
    """
    @property
    def __key_type_details(self, /) -> Any | None: ...
    def __list_keys(self, /) -> list[int]: ...
    @property
    def attributes(self, /) -> AttributeSet:
        """
        Returns the `AttributeSet` defined in the `Service`.
        """
    def blocking_cleanup_dead_nodes(self, /, timeout: Duration) -> Any:
        """
        Removes the stale system resources of every dead `Node` connected to this service.

        If a `Node` cannot be cleaned up since the process has insufficient permissions then the
        `Node` is skipped. If it is currently being cleaned up by another process then the
        cleaner will wait until the timeout as either passed or the cleaned was finished.

        The timeout is applied to every individual dead `Node` the function needs to wait on.
        """
    def delete(self, /) -> None:
        """
        Releases the `PortFactoryBlackboard`.

        After this call the `PortFactoryBlackboard` is no longer usable!
        """
    @property
    def dynamic_config(self, /) -> DynamicConfigBlackboard:
        """
        Returns the dynamic configuration, including the current port counts.
        """
    @property
    def name(self, /) -> ServiceName:
        """
        Returns the `ServiceName` of the service.
        """
    @property
    def nodes(self, /) -> list[NodeState]:
        """
        Returns a list of all `NodeState` of every `Node` which has opened the `Service`.
        """
    def reader_builder(self, /) -> PortFactoryReader:
        """
        Returns a `PortFactoryReader` to create a new `Reader` port
        """
    @property
    def service_hash(self, /) -> ServiceHash:
        """
        Returns the `ServiceHash` of the `Service`.
        """
    @property
    def static_config(self, /) -> StaticConfigBlackboard:
        """
        Returns the StaticConfig of the `Service`. Contains all settings that never change during
        the lifetime of the service.
        """
    def try_cleanup_dead_nodes(self, /) -> Any:
        """
        Removes the stale system resources of every dead `Node` connected to this service.

        If a `Node` cannot be cleaned up since the process has insufficient permissions or it
        is currently being cleaned up by another process then the `Node` is skipped.
        """
    def writer_builder(self, /) -> PortFactoryWriter:
        """
        Returns a `PortFactoryWriter` to create a new `Writer` port
        """

@final
class PortFactoryClient:
    """
    Factory to create a new `Client` port/endpoint for `MessagingPattern.RequestResponse`
    based communication.
    """
    def __allocation_strategy(self, /, value: AllocationStrategy) -> PortFactoryClient2:
        """
        Defines the allocation strategy that is used when the provided
        `PortFactoryClient.initial_max_slice_len` is exhausted. This happens when the user
        acquires more than max slice len in `Client.loan_slice` or `Client.loan_slice_uninit`.
        """
    def __initial_max_slice_len(self, /, value: int) -> PortFactoryClient2:
        """
        Sets the maximum slice length that a user can allocate with
        `Client.loan_slice` or `Client.loan_slice_uninit`.
        """
    @property
    def __request_header_type_details(self, /) -> Any | None: ...
    @property
    def __request_payload_type_details(self, /) -> Any | None: ...
    @property
    def __response_header_type_details(self, /) -> Any | None: ...
    @property
    def __response_payload_type_details(self, /) -> Any | None: ...
    def backpressure_strategy(self, /, value: BackpressureStrategy) -> PortFactoryClient2:
        """
        Sets the `BackpressureStrategy` which defines how the `Client` shall behave
        when a `Server` cannot receive a `RequestMut` since its internal buffer is full.
        """
    def create(self, /) -> Client2:
        """
        Creates a new `Client` or emits a `ClientCreateError` on failure.
        """
    def max_active_requests(self, /, value: int) -> PortFactoryClient2:
        """
        Defines the maximal active requests the `Client` can send. Smallest possible value is ``1``.
        """
    def name(self, /, value: PortName) -> PortFactoryClient2:
        """
        The `PortName` that shall be assigned to the `Client`. It does not
        have to be unique. If no `PortName` is defined then the `Client`
        does not have a name.
        """
    def override_request_preallocation(self, /, value: int) -> PortFactoryClient2:
        """
        Reduces the preallocated `RequestMut` count.
        The return value is clamped between ``1`` and the worst case
        preallocated `RequestMut` count required
        to guarantee that the `Client` always has a `RequestMut` to loan
        and send.

        # Important

        If the user reduces the preallocated `RequestMut` count, iceoryx2 can
        no longer guarantee, that the `Client` can always loan a `RequestMut`
        to send.
        """

@final
class PortFactoryEvent:
    """
    The factory for `MessagingPattern.Event`. It can acquire dynamic and static service
    information and create `Notifier` or `Listener` ports.
    """
    @property
    def attributes(self, /) -> AttributeSet:
        """
        Returns the `AttributeSet` defined in the `Service`
        """
    def blocking_cleanup_dead_nodes(self, /, timeout: Duration) -> Any:
        """
        Removes the stale system resources of every dead `Node` connected to this service.

        If a `Node` cannot be cleaned up since the process has insufficient permissions then the
        `Node` is skipped. If it is currently being cleaned up by another process then the
        cleaner will wait until the timeout as either passed or the cleaned was finished.

        The timeout is applied to every individual dead `Node` the function needs to wait on.
        """
    @property
    def dynamic_config(self, /) -> DynamicConfigEvent:
        """
        Returns the dynamic configuration, including the current port counts.
        """
    def listener_builder(self, /) -> PortFactoryListener:
        """
        Returns a `PortFactoryListener` to create a new `Listener` port
        """
    @property
    def name(self, /) -> ServiceName:
        """
        Returns the `ServiceName` of the service
        """
    @property
    def nodes(self, /) -> list[NodeState]:
        """
        Returns a list of all `NodeState` of every `Node` which has opened the `Service`.
        """
    def notifier_builder(self, /) -> PortFactoryNotifier:
        """
        Returns a `PortFactoryNotifier` to create a new `Notifier` port
        """
    @property
    def service_hash(self, /) -> ServiceHash:
        """
        Returns the `ServiceHash` of the `Service`
        """
    @property
    def static_config(self, /) -> StaticConfigEvent:
        """
        Returns the StaticConfig of the `Service`.
        Contains all settings that never change during the lifetime of the service.
        """
    def try_cleanup_dead_nodes(self, /) -> Any:
        """
        Removes the stale system resources of every dead `Node` connected to this service.

        If a `Node` cannot be cleaned up since the process has insufficient permissions or it
        is currently being cleaned up by another process then the `Node` is skipped.
        """

@final
class PortFactoryListener:
    """
    Factory to create a new `Listener` port/endpoint for `MessagingPattern.Event` based
    communication.
    """
    def create(self, /) -> Listener:
        """
        Creates the `Listener` port or emits a `ListenerCreateError` on failure.
        """
    def name(self, /, value: PortName) -> PortFactoryListener:
        """
        The `PortName` that shall be assigned to the `Listener`. It does not
        have to be unique. If no `PortName` is defined then the `Listener`
        does not have a name.
        """

@final
class PortFactoryNotifier:
    """
    Factory to create a new `Notifier` port/endpoint for `MessagingPattern.Event` based
    communication.
    """
    def create(self, /) -> Notifier:
        """
        Creates a new `Notifier` port or emits a `NotifierCreateError` on failure.
        """
    def default_event_id(self, /, value: EventId) -> PortFactoryNotifier:
        """
        Sets a default `EventId` for the `Notifier` that is used in `Notifier.notify()`
        """
    def name(self, /, value: PortName) -> PortFactoryNotifier:
        """
        The `PortName` that shall be assigned to the `Notifier`. It does not
        have to be unique. If no `PortName` is defined then the `Notifier`
        does not have a name.
        """

@final
class PortFactoryPublishSubscribe:
    """
    The factory for `MessagingPattern.PublishSubscribe`. It can acquire dynamic and static service
    information and create `Publisher` or `Subscriber` ports.
    """
    @property
    def attributes(self, /) -> AttributeSet:
        """
        Returns the `AttributeSet` defined in the `Service`
        """
    def blocking_cleanup_dead_nodes(self, /, timeout: Duration) -> Any:
        """
        Removes the stale system resources of every dead `Node` connected to this service.

        If a `Node` cannot be cleaned up since the process has insufficient permissions then the
        `Node` is skipped. If it is currently being cleaned up by another process then the
        cleaner will wait until the timeout as either passed or the cleaned was finished.

        The timeout is applied to every individual dead `Node` the function needs to wait on.
        """
    @property
    def dynamic_config(self, /) -> DynamicConfigPublishSubscribe:
        """
        Returns the dynamic configuration, including the current port counts.
        """
    @property
    def name(self, /) -> ServiceName:
        """
        Returns the `ServiceName` of the service
        """
    @property
    def nodes(self, /) -> list[NodeState]:
        """
        Returns a list of all `NodeState` of every `Node` which has opened the `Service`.
        """
    def publisher_builder(self, /) -> PortFactoryPublisher2:
        """
        Returns a `PortFactoryPublisher` to create a new `Publisher` port
        """
    @property
    def service_hash(self, /) -> ServiceHash:
        """
        Returns the `ServiceHash` of the `Service`
        """
    @property
    def static_config(self, /) -> StaticConfigPublishSubscribe:
        """
        Returns the StaticConfig of the `Service`.
        Contains all settings that never change during the lifetime of the service.
        """
    def subscriber_builder(self, /) -> PortFactorySubscriber:
        """
        Returns a `PortFactorySubscriber` to create a new `Subscriber` port
        """
    def try_cleanup_dead_nodes(self, /) -> Any:
        """
        Removes the stale system resources of every dead `Node` connected to this service.

        If a `Node` cannot be cleaned up since the process has insufficient permissions or it
        is currently being cleaned up by another process then the `Node` is skipped.
        """

@final
class PortFactoryPublisher:
    """
    Factory to create a new `Publisher` port/endpoint for `MessagingPattern.PublishSubscribe`
    based communication.
    """
    def __allocation_strategy(self, /, value: AllocationStrategy) -> PortFactoryPublisher2:
        """
        Defines the allocation strategy that is used when the provided
        `PortFactoryServer.initial_max_slice_len` is exhausted. This happens when the user
        acquires more than max slice len in `ActiveRequest.loan_slice` or
        `ActiveRequest.loan_slice_uninit`.
        """
    def __initial_max_slice_len(self, /, value: int) -> PortFactoryPublisher2:
        """
        Sets the maximum slice length that a user can allocate with
        `ActiveRequest.loan_slice` or `ActiveRequest.loan_slice_uninit`.
        """
    @property
    def __payload_type_details(self, /) -> Any | None: ...
    def backpressure_strategy(self, /, value: BackpressureStrategy) -> PortFactoryPublisher2:
        """
        Sets the `BackpressureStrategy`.
        """
    def create(self, /) -> Publisher2:
        """
        Creates a new `Publisher` or emits a `PublisherCreateError` on failure.
        """
    def max_loaned_samples(self, /, value: int) -> PortFactoryPublisher2:
        """
        Defines how many `SampleMut` the `Publisher` can loan with `Publisher.loan_uninit` or
        `Publisher.loan_slice_uninit` in parallel.
        """
    def name(self, /, value: PortName) -> PortFactoryPublisher2:
        """
        The `PortName` that shall be assigned to the `Publisher`. It does not
        have to be unique. If no `PortName` is defined then the `Publisher`
        does not have a name.
        """
    def override_sample_preallocation(self, /, value: int) -> PortFactoryPublisher2:
        """
        Reduces the preallocated `SampleMut` count.
        The return value is clamped between ``1`` and the worst case
        preallocated `SampleMut` count required
        to guarantee that the `Publisher` always has a `SampleMut` to loan
        and send.

        # Important

        If the user reduces the preallocated `SampleMut` count, iceoryx2 can
        no longer guarantee, that the `Publisher` can always loan a `SampleMut`
        to send.
        """

@final
class PortFactoryReader:
    """
    Factory to create a new `Reader` port/endpoint for `MessagingPattern.Blackboard`
    based communication.
    """
    def create(self, /) -> Reader2:
        """
        Creates a new `Reader` or emits a `ReaderCreateError` on failure.
        """
    def name(self, /, value: PortName) -> PortFactoryReader:
        """
        The `PortName` that shall be assigned to the `Reader`. It does not
        have to be unique. If no `PortName` is defined then the `Reader`
        does not have a name.
        """

@final
class PortFactoryRequestResponse:
    """
    The factory for `MessagingPattern.RequestResponse`. It can acquire dynamic and static service
    information and create `Client` or `Server` ports.
    """
    @property
    def attributes(self, /) -> AttributeSet:
        """
        Returns the `AttributeSet` defined in the `Service`
        """
    def blocking_cleanup_dead_nodes(self, /, timeout: Duration) -> Any:
        """
        Removes the stale system resources of every dead `Node` connected to this service.

        If a `Node` cannot be cleaned up since the process has insufficient permissions then the
        `Node` is skipped. If it is currently being cleaned up by another process then the
        cleaner will wait until the timeout as either passed or the cleaned was finished.

        The timeout is applied to every individual dead `Node` the function needs to wait on.
        """
    def client_builder(self, /) -> PortFactoryClient2:
        """
        Returns a `PortFactoryClient` to create a new `Client` port
        """
    @property
    def dynamic_config(self, /) -> DynamicConfigRequestResponse:
        """
        Returns the dynamic configuration, including the current port counts.
        """
    @property
    def name(self, /) -> ServiceName:
        """
        Returns the `ServiceName` of the service
        """
    @property
    def nodes(self, /) -> list[NodeState]:
        """
        Returns a list of all `NodeState` of every `Node` which has opened the `Service`.
        """
    def server_builder(self, /) -> PortFactoryServer2:
        """
        Returns a `PortFactoryServer` to create a new `Server` port
        """
    @property
    def service_hash(self, /) -> ServiceHash:
        """
        Returns the `ServiceHash` of the `Service`
        """
    @property
    def static_config(self, /) -> StaticConfigRequestResponse:
        """
        Returns the StaticConfig of the `Service`.
        Contains all settings that never change during the lifetime of the service.
        """
    def try_cleanup_dead_nodes(self, /) -> Any:
        """
        Removes the stale system resources of every dead `Node` connected to this service.

        If a `Node` cannot be cleaned up since the process has insufficient permissions or it
        is currently being cleaned up by another process then the `Node` is skipped.
        """

@final
class PortFactoryServer:
    """
    Factory to create a new `Server` port/endpoint for `MessagingPattern.RequestResponse` based
    communication.
    """
    def __allocation_strategy(self, /, value: AllocationStrategy) -> PortFactoryServer2:
        """
        Defines the allocation strategy that is used when the provided
        `PortFactoryServer.initial_max_slice_len` is exhausted. This happens when the user
        acquires more than max slice len in `ActiveRequest.loan_slice` or
        `ActiveRequest.loan_slice_uninit`.
        """
    def __initial_max_slice_len(self, /, value: int) -> PortFactoryServer2:
        """
        Sets the maximum slice length that a user can allocate with
        `ActiveRequest.loan_slice` or `ActiveRequest.loan_slice_uninit`.
        """
    @property
    def __request_header_type_details(self, /) -> Any | None: ...
    @property
    def __request_payload_type_details(self, /) -> Any | None: ...
    @property
    def __response_header_type_details(self, /) -> Any | None: ...
    @property
    def __response_payload_type_details(self, /) -> Any | None: ...
    def backpressure_strategy(self, /, value: BackpressureStrategy) -> PortFactoryServer2:
        """
        Sets the `BackpressureStrategy` which defines how the `Server` shall behave
        when a `Client` cannot receive a `Response` since its internal buffer is full.
        """
    def create(self, /) -> Server:
        """
        Creates a new `Server` or emits a `ServerCreateError` on failure.
        """
    def max_loaned_responses_per_request(self, /, value: int) -> PortFactoryServer2:
        """
        Defines the maximum number of `ResponseMut` that
        the `Server` can loan in parallel per
        `ActiveRequest`.
        """
    def name(self, /, value: PortName) -> PortFactoryServer2:
        """
        The `PortName` that shall be assigned to the `Server`. It does not
        have to be unique. If no `PortName` is defined then the `Server`
        does not have a name.
        """
    def override_response_preallocation(self, /, value: int) -> PortFactoryServer2:
        """
        Reduces the preallocated `ResponseMut` count.
        The return value is clamped between ``1`` and the worst case
        preallocated `ResponseMut` count required
        to guarantee that the `Server` always has a `ResponseMut` to loan
        and send.

        # Important

        If the user reduces the preallocated `ResponseMut` count, iceoryx2 can
        no longer guarantee, that the `Server` can always loan a `ResponseMut`
        to send.
        """

@final
class PortFactorySubscriber:
    """
    Factory to create a new `Subscriber` port/endpoint for
    `MessagingPattern.PublishSubscribe` based communication.
    """
    def buffer_size(self, /, value: int) -> PortFactorySubscriber:
        """
        Defines the buffer size of the `Subscriber`. Smallest possible value is ``1``.
        """
    def create(self, /) -> Subscriber:
        """
        Creates a new `Subscriber` or emits a `SubscriberCreateError` on failure.
        """
    def history_request(self, /, value: int) -> PortFactorySubscriber:
        """
        Defines the amount of requested history samples. By default the value defined with the
        service's ``history_size`` is used
        """
    def name(self, /, value: PortName) -> PortFactorySubscriber:
        """
        The `PortName` that shall be assigned to the `Subscriber`. It does not
        have to be unique. If no `PortName` is defined then the `Subscriber`
        does not have a name.
        """

@final
class PortFactoryWriter:
    """
    Factory to create a new `Writer` port/endpoint for `MessagingPattern.Blackboard`
    based communication.
    """
    def create(self, /) -> Writer2:
        """
        Creates a new `Writer` or returns a `WriterCreateError` on failure.
        """
    def name(self, /, value: PortName) -> PortFactoryWriter:
        """
        The `PortName` that shall be assigned to the `Writer`. It does not
        have to be unique. If no `PortName` is defined then the `Writer`
        does not have a name.
        """

@final
class PortName:
    """
    Represent the name for a port.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    def as_str(self, /) -> str:
        """
        Converts the `PortName` into a `str`
        """
    @staticmethod
    def max_len() -> int:
        """
        Returns the maximum length of a `PortName`
        """
    @staticmethod
    def new(name: str) -> PortName:
        """
        Creates a new `PortName`.
        If the provided name does not contain a valid `PortName` it will emit
        `SemanticStringError`, otherwise the `PortName`.
        """

@final
class Publisher:
    """
    Represents the receiving endpoint of an event based communication.
    """
    def __loan_slice_uninit(self, /, number_of_elements: int) -> SampleMutUninit2:
        """
        Loans/allocates a `SampleMutUninit` from the underlying data segment of the `Publisher`.
        The user has to initialize the payload before it can be sent.
        Fails when it is called for data types which are not a slice.

        On failure it returns `LoanError` describing the failure.
        """
    def __loan_uninit(self, /) -> SampleMutUninit2:
        """
        Loans/allocates a `SampleMutUninit` from the underlying data segment of the `Publisher`.
        The user has to initialize the payload before it can be sent.

        On failure it returns `LoanError` describing the failure.
        """
    @property
    def __payload_type_details(self, /) -> Any | None: ...
    @property
    def backpressure_strategy(self, /) -> BackpressureStrategy:
        """
        Returns the strategy the `Publisher` follows when a `SampleMut` cannot be delivered
        since the `Subscriber`'s buffer is full.
        """
    def delete(self, /) -> None:
        """
        Releases the `Publisher`.

        After this call the `Publisher` is no longer usable!
        """
    @property
    def id(self, /) -> UniquePublisherId:
        """
        Returns the `UniquePublisherId` of the `Publisher`
        """
    @property
    def initial_max_slice_len(self, /) -> int:
        """
        Returns the maximum initial slice length configured for this `Publisher`.
        """
    @property
    def name(self, /) -> PortName:
        """
        Returns the `PortName` of the `Publisher`
        """
    def update_connections(self, /) -> None:
        """
        Explicitly updates the connection to every `Subscriber`. This is
        required to be called whenever a new `Subscriber` connected to
        the service. It is done implicitly whenever `SampleMut.send` or
        `Publisher.send_copy` is called. When a `Subscriber` is connected
        that requires a history this call will deliver it.
        """

@final
class Reader:
    """
    Represents the reading endpoint of a blackboard based communication.
    """
    def __entry(self, /, key: int, value_type_details: TypeDetail) -> EntryHandle2:
        """
        Creates an EntryHandle for direct read access to the value. On failure
        it returns `EntryHandleError` describing the failure.
        """
    @property
    def __key_type_details(self, /) -> Any | None: ...
    def delete(self, /) -> None:
        """
        Releases the `Reader`.

        After this call the `Reader` is no longer usable!
        """
    @property
    def id(self, /) -> UniqueReaderId:
        """
        Returns the `UniqueReaderId` of the `Reader`
        """
    @property
    def name(self, /) -> PortName:
        """
        Returns the `PortName` of the `Reader`
        """

@final
class RequestHeader:
    """
    Request header used by `MessagingPattern.RequestResponse`
    """
    def __str__(self, /) -> str: ...
    @property
    def client_id(self, /) -> UniqueClientId:
        """
        Returns the `UniqueClientId` of the `Client` which sent the `RequestMut`
        """
    @property
    def number_of_elements(self, /) -> int:
        """
        Returns how many elements are stored inside the requests's payload.
        """
    @property
    def payload_offset(self, /) -> int:
        """
        Returns the payload offset.
        """

@final
class RequestMut:
    """
    The `RequestMut` represents the object that contains the payload that the `Client` sends to the
    `Server`.
    """
    @property
    def __request_header_type_details(self, /) -> Any | None: ...
    @property
    def __request_payload_type_details(self, /) -> Any | None: ...
    @property
    def __response_header_type_details(self, /) -> Any | None: ...
    @property
    def __response_payload_type_details(self, /) -> Any | None: ...
    @property
    def __slice_len(self, /) -> int: ...
    def delete(self, /) -> None:
        """
        Releases the `RequestMut`.

        After this call the `RequestMut` is no longer usable!
        """
    @property
    def header(self, /) -> RequestHeader:
        """
        Returns the iceoryx2 internal `RequestHeader`
        """
    @property
    def payload_ptr(self, /) -> int:
        """
        Returns the address of the user defined request payload as an `int`.
        `RequestMut.payload` provides typed access.
        """
    def send(self, /) -> PendingResponse2:
        """
        Sends the `RequestMut` to every connected `Server` of the `Service`.
        """
    @property
    def user_header_ptr(self, /) -> int:
        """
        Returns the address of the user defined request header as an `int`.
        `RequestMut.user_header` provides typed access.
        """

@final
class RequestMutUninit:
    """
    A version of the `RequestMut` where the payload is not initialized which allows
    true zero copy usage. To send a `RequestMutUninit` it must be first initialized
    and converted into `RequestMut` with `RequestMutUninit.assume_init`.
    """
    def __assume_init(self, /) -> RequestMut2: ...
    def __assume_init_flatbuffer(self, /, buffer_ptr: int, buffer_len: int, payload_offset: int) -> RequestMut2: ...
    @property
    def __available_payload_memory(self, /) -> int: ...
    @property
    def __request_header_type_details(self, /) -> Any | None: ...
    @property
    def __request_payload_type_details(self, /) -> Any | None: ...
    @property
    def __response_header_type_details(self, /) -> Any | None: ...
    @property
    def __response_payload_type_details(self, /) -> Any | None: ...
    @property
    def __slice_len(self, /) -> int: ...
    def delete(self, /) -> None:
        """
        Releases the `RequestMutUninit`.

        After this call the `RequestMutUninit` is no longer usable!
        """
    @property
    def header(self, /) -> RequestHeader:
        """
        Returns the iceoryx2 internal `RequestHeader`
        """
    @property
    def payload_ptr(self, /) -> int:
        """
        Returns the address of the user defined request payload as an `int`.
        `RequestMutUninit.payload` provides typed access.
        """
    @property
    def user_header_ptr(self, /) -> int:
        """
        Returns the address of the user defined request header as an `int`.
        `RequestMutUninit.user_header` provides typed access.
        """

@final
class Response:
    """
    It stores the payload and can be received by the `PendingResponse` after a `RequestMut` was
    sent to a `Server` via the `Client`.
    """
    @property
    def __response_header_type_details(self, /) -> Any | None: ...
    @property
    def __response_payload_type_details(self, /) -> Any | None: ...
    @property
    def __slice_len(self, /) -> int: ...
    def delete(self, /) -> None:
        """
        Releases the `Response`.

        After this call the `Response` is no longer usable!
        """
    @property
    def header(self, /) -> ResponseHeader:
        """
        Returns the `ResponseHeader`
        """
    @property
    def origin(self, /) -> UniqueServerId:
        """
        Returns the `UniqueServerId` of the `Server` which sent the `Response`.
        """
    @property
    def payload_ptr(self, /) -> int:
        """
        Returns the address of the payload of the response as an `int`.
        `Response.payload` provides typed access.
        """
    @property
    def user_header_ptr(self, /) -> int:
        """
        Returns the address of the user header of the response as an `int`.
        `Response.user_header` provides typed access.
        """

@final
class ResponseHeader:
    """
    Response header used by `MessagingPattern.RequestResponse`
    """
    def __str__(self, /) -> str: ...
    @property
    def number_of_elements(self, /) -> int:
        """
        Returns how many elements are stored inside the `Response`'s payload.
        """
    @property
    def payload_offset(self, /) -> int:
        """
        Returns the payload offset.
        """
    @property
    def server_id(self, /) -> UniqueServerId:
        """
        Returns the `UniqueServerId` of the `Server` which sent the `Response`
        """

@final
class ResponseMut:
    @property
    def __response_header_type_details(self, /) -> Any | None: ...
    @property
    def __response_payload_type_details(self, /) -> Any | None: ...
    @property
    def __slice_len(self, /) -> int: ...
    def delete(self, /) -> None:
        """
        Releases the `ResponseMut`.

        After this call the `ResponseMut` is no longer usable!
        """
    @property
    def header(self, /) -> ResponseHeader:
        """
        Returns a reference to the `ResponseHeader`.
        """
    @property
    def payload_ptr(self, /) -> int:
        """
        Returns the address of the payload of the response as an `int`.
        `ResponseMut.payload` provides typed access.
        """
    def send(self, /) -> None:
        """
        Sends a `ResponseMut` to the corresponding `PendingResponse` of the
        `Client`.
        """
    @property
    def user_header_ptr(self, /) -> int:
        """
        Returns the address of the user header of the response as an `int`.
        `ResponseMut.user_header` provides typed access.
        """

@final
class ResponseMutUninit:
    """
    Acquired by an `ActiveRequest` with
     * `ActiveRequest.loan_uninit`,
     * `ActiveRequest.loan_slice_uninit`,
     * `ActiveRequest.loan_flatbuffer`

    It stores the uninitialized payload of the response. It must be initialized and converted
    into a `ResponseMut` with `ResponseMutUninit.write_payload` or
    `ResponseMutUninit.assume_init` before it can be sent. Otherwise the loaned memory is
    released when going out of scope.
    """
    def __assume_init(self, /) -> ResponseMut2: ...
    def __assume_init_flatbuffer(self, /, buffer_ptr: int, buffer_len: int, payload_offset: int) -> ResponseMut2: ...
    @property
    def __available_payload_memory(self, /) -> int: ...
    @property
    def __response_header_type_details(self, /) -> Any | None: ...
    @property
    def __response_payload_type_details(self, /) -> Any | None: ...
    @property
    def __slice_len(self, /) -> int: ...
    def delete(self, /) -> None:
        """
        Releases the `ResponseMutUninit`.

        After this call the `ResponseMutUninit` is no longer usable!
        """
    @property
    def header(self, /) -> ResponseHeader:
        """
        Returns a reference to the `ResponseHeader`.
        """
    @property
    def payload_ptr(self, /) -> int:
        """
        Returns the address of the payload of the response as an `int`.
        `ResponseMutUninit.payload` provides typed access.
        """
    @property
    def user_header_ptr(self, /) -> int:
        """
        Returns the address of the user header of the response as an `int`.
        `ResponseMutUninit.user_header` provides typed access.
        """

@final
class Sample:
    """
    It stores the payload and is acquired by the `Subscriber` whenever
    it receives new data from a `Publisher` via `Subscriber.receive`.
    """
    @property
    def __payload_type_details(self, /) -> Any | None: ...
    @property
    def __slice_len(self, /) -> int: ...
    @property
    def __user_header_type_details(self, /) -> Any | None: ...
    def delete(self, /) -> None:
        """
        Releases the `Sample`.

        After this call the `Sample` is no longer usable!
        """
    @property
    def header(self, /) -> HeaderPublishSubscribe:
        """
        Returns the `HeaderPublishSubscribe` of the `Sample`.
        """
    @property
    def payload_ptr(self, /) -> int:
        """
        Returns the address of the payload as an `int`.
        `Sample.payload` provides typed access.
        """
    @property
    def user_header_ptr(self, /) -> int:
        """
        Returns the address of the user header as an `int`.
        `Sample.user_header` provides typed access.
        """

@final
class SampleMut:
    """
    Acquired by initializing a `SampleMutUninit` via
     * `SampleMutUninit.write_payload`,
     * `SampleMutUninit.assume_init`

    It stores the payload that will be sent
    to every connected `Subscriber`. If the `SampleMut` is not sent
    it will release the loaned memory when going out of scope.
    """
    @property
    def __payload_type_details(self, /) -> Any | None: ...
    @property
    def __slice_len(self, /) -> int: ...
    def __truncate(self, /, number_of_elements: int) -> None: ...
    @property
    def __user_header_type_details(self, /) -> Any | None: ...
    def delete(self, /) -> None:
        """
        Releases the `SampleMut`.

        After this call the `SampleMut` is no longer usable!
        """
    @property
    def header(self, /) -> HeaderPublishSubscribe:
        """
        Returns the `HeaderPublishSubscribe` of the `Sample`.
        """
    @property
    def payload_ptr(self, /) -> int:
        """
        Returns the address of the payload as an `int`.
        `SampleMut.payload` provides typed access.
        """
    def send(self, /) -> int:
        """
        Send a previously loaned `Publisher.loan_uninit` `SampleMut` to every connected
        `Subscriber` of the service.

        On success the number of `Subscriber` ports that received
        the data is returned, otherwise a `SendError` is emitted describing the failure.
        """
    @property
    def user_header_ptr(self, /) -> int:
        """
        Returns the address of the user header as an `int`.
        `SampleMut.user_header` provides typed access.
        """

@final
class SampleMutUninit:
    """
    Acquired by a `Publisher` via
     * `Publisher.loan_uninit`,
     * `Publisher.loan_slice_uninit`,
     * `Publisher.loan_flatbuffer`

    It stores the uninitialized payload. It must be initialized and converted into a
    `SampleMut` with `SampleMutUninit.write_payload` or `SampleMutUninit.assume_init`
    before it can be sent. Otherwise the loaned memory is released when going out of scope.
    """
    def __assume_init(self, /) -> SampleMut2: ...
    def __assume_init_flatbuffer(self, /, buffer_ptr: int, buffer_len: int, payload_offset: int) -> SampleMut2: ...
    @property
    def __available_payload_memory(self, /) -> int: ...
    @property
    def __payload_type_details(self, /) -> Any | None: ...
    @property
    def __slice_len(self, /) -> int: ...
    def __truncate(self, /, number_of_elements: int) -> None: ...
    @property
    def __user_header_type_details(self, /) -> Any | None: ...
    def delete(self, /) -> None:
        """
        Releases the `SampleMutUninit`.

        After this call the `SampleMutUninit` is no longer usable!
        """
    @property
    def header(self, /) -> HeaderPublishSubscribe:
        """
        Returns the `HeaderPublishSubscribe` of the `Sample`.
        """
    @property
    def payload_ptr(self, /) -> int:
        """
        Returns the address of the payload as an `int`.
        `SampleMutUninit.payload` provides typed access.
        """
    @property
    def user_header_ptr(self, /) -> int:
        """
        Returns the address of the user header as an `int`.
        `SampleMutUninit.user_header` provides typed access.
        """

@final
class Server:
    """
    Represents the receiving endpoint of an event based communication.
    """
    @property
    def __initial_max_slice_len(self, /) -> int:
        """
        Returns the maximum initial slice length configured for this `Server`.
        """
    @property
    def __request_header_type_details(self, /) -> Any | None: ...
    @property
    def __request_payload_type_details(self, /) -> Any | None: ...
    @property
    def __response_header_type_details(self, /) -> Any | None: ...
    @property
    def __response_payload_type_details(self, /) -> Any | None: ...
    @property
    def backpressure_strategy(self, /) -> BackpressureStrategy:
        """
        Returns the strategy the `Server` follows when a `ResponseMut` cannot be delivered
        if the `Client`'s buffer is full.
        """
    def delete(self, /) -> None:
        """
        Releases the `Server`.

        After this call the `Server` is no longer usable!
        """
    @property
    def has_requests(self, /) -> bool:
        """
        Returns true if the `Server` has a `RequestMut` in its buffer.
        """
    @property
    def id(self, /) -> UniqueServerId:
        """
        Returns the `UniqueServerId` of the `Server`
        """
    @property
    def name(self, /) -> PortName:
        """
        Returns the `PortName` of the `Server`
        """
    def receive(self, /) -> ActiveRequest2 | None:
        """
        Receives a `RequestMut` that was sent by a `Client` and returns an `ActiveRequest`
        which can be used to respond. If no `RequestMut` was received it returns `None`.
        """

@final
class Service:
    """
    Builder to create or open a `Service`
    """
    @staticmethod
    def details(service_name: ServiceName, config: Config, messaging_pattern: MessagingPattern, service_type: ServiceType) -> ServiceDetails | None:
        """
        Acquires the `ServiceDetails` of a `Service`.
        """
    @staticmethod
    def does_exist(service_name: ServiceName, config: Config, messaging_pattern: MessagingPattern, service_type: ServiceType) -> bool:
        """
        Checks if a service under a given `config.Config` does exist
        """
    @staticmethod
    def list(config: Config, service_type: ServiceType) -> list[ServiceDetails]:
        """
        Returns a list of all services created under a given `config.Config`.
        """

@final
class ServiceBuilder:
    """
    Builder to create or open a `Service`
    """
    def __blackboard_creator(self, /) -> ServiceBuilderBlackboardCreator2:
        """
        Create a new builder to create a `MessagingPattern.Blackboard` `Service`.
        """
    def __blackboard_opener(self, /) -> ServiceBuilderBlackboardOpener:
        """
        Create a new builder to open a `MessagingPattern.Blackboard` `Service`.
        """
    def __publish_subscribe(self, /) -> ServiceBuilderPublishSubscribe2:
        """
        Create a new builder to create a `MessagingPattern.PublishSubscribe` `Service`.
        """
    def __request_response(self, /) -> ServiceBuilderRequestResponse2:
        """
        Create a new builder to create a `MessagingPattern.RequestResponse` `Service`.
        """
    def event(self, /) -> ServiceBuilderEvent:
        """
        Create a new builder to create a `MessagingPattern.Event` `Service`.
        """

@final
class ServiceBuilderBlackboardCreator:
    """
    Builder to create a new `MessagingPattern.Blackboard` based `Service`
    """
    def __add(self, /, key: int, value: int, value_details: TypeDetail) -> ServiceBuilderBlackboardCreator2:
        """
        Adds key-value pairs to the blackboard.
        """
    @property
    def __key_type_details(self, /) -> Any | None: ...
    def __set_key_eq_cmp_func(self, /, key_eq_func: Any) -> ServiceBuilderBlackboardCreator2:
        """
        Defines the key eq comparison function needed to store and retrieve keys in the
        blackboard.
        """
    def __set_key_type(self, /, value: Any) -> None: ...
    def __set_key_type_details(self, /, value: TypeDetail) -> ServiceBuilderBlackboardCreator2:
        """
        Defines the key type. To be able to connect to a `Service`, the `TypeDetail` must be
        identical in all participants since the communication is always strongly typed.
        """
    def create(self, /) -> PortFactoryBlackboard2:
        """
        Creates a new `Service`.
        """
    def create_with_attributes(self, /, attributes: AttributeSpecifier) -> PortFactoryBlackboard2:
        """
        Creates a new `Service` with a set of attributes.
        """
    def max_nodes(self, /, value: int) -> ServiceBuilderBlackboardCreator2:
        """
        Defines how many `Node` instances shall be able to open the `Service` in parallel.
        """
    def max_readers(self, /, value: int) -> ServiceBuilderBlackboardCreator2:
        """
        Defines how many `Reader` ports shall be supported at most.
        """

@final
class ServiceBuilderBlackboardOpener:
    """
    Builder to open a new `MessagingPattern.Blackboard` based `Service`
    """
    @property
    def __key_type_details(self, /) -> Any | None: ...
    def __set_key_eq_cmp_func(self, /, key_eq_func: Any) -> ServiceBuilderBlackboardOpener:
        """
        Defines the key eq comparison function needed to store and retrieve keys in the
        blackboard.
        """
    def __set_key_type(self, /, value: Any) -> None: ...
    def __set_key_type_details(self, /, value: TypeDetail) -> ServiceBuilderBlackboardOpener:
        """
        Defines the key type. To be able to connect to a `Service`, the `TypeDetail` must be
        identical in all participants since the communication is always strongly typed.
        """
    def max_nodes(self, /, value: int) -> ServiceBuilderBlackboardOpener:
        """
        Defines how many `Node` instances must be at least supported.
        """
    def max_readers(self, /, value: int) -> ServiceBuilderBlackboardOpener:
        """
        Defines how many `Reader` ports must be at least supported.
        """
    def open(self, /) -> PortFactoryBlackboard2:
        """
        Opens an existing `Service`.
        """
    def open_with_attributes(self, /, verifier: AttributeVerifier) -> PortFactoryBlackboard2:
        """
        Opens an existing `Service` with attribute requirements. If the defined attribute
        requirements are not satisfied the open process will fail.
        """

@final
class ServiceBuilderEvent:
    """
    Builder to create a new `MessagingPattern.Event` based `Service`
    """
    def create(self, /) -> PortFactoryEvent:
        """
        Creates a new `Service`.
        """
    def create_with_attributes(self, /, attributes: AttributeSpecifier) -> PortFactoryEvent:
        """
        Creates a new `Service` with a set of attributes.
        """
    def deadline(self, /, deadline: Duration) -> ServiceBuilderEvent:
        """
        Enables the deadline property of the service. There must be a notification emitted by any
        `Notifier` after at least the provided `deadline`.
        """
    def disable_deadline(self, /) -> ServiceBuilderEvent:
        """
        Disables the deadline property of the service. `Notifier` can signal notifications at any
        rate.
        """
    def disable_notifier_created_event(self, /) -> ServiceBuilderEvent:
        """
        If the `Service` is created it disables the event that shall be emitted by every newly
        created `Notifier`.
        """
    def disable_notifier_dead_event(self, /) -> ServiceBuilderEvent:
        """
        If the `Service` is created it disables the event that shall be emitted when a
        `Notifier` is identified as dead.
        """
    def disable_notifier_dropped_event(self, /) -> ServiceBuilderEvent:
        """
        If the `Service` is created it disables the event that shall be emitted by every
        `Notifier` before it is dropped.
        """
    def event_id_max_value(self, /, value: int) -> ServiceBuilderEvent:
        """
        If the `Service` is created it set the greatest supported `EventId` value
        If an existing `Service` is opened it defines the value size the `EventId`
        must at least support.
        """
    def max_listeners(self, /, value: int) -> ServiceBuilderEvent:
        """
        If the `Service` is created it defines how many `Listener` shall be supported at most. If
        an existing `Service` is opened it defines how many `Listener` must be at least supported.
        """
    def max_nodes(self, /, value: int) -> ServiceBuilderEvent:
        """
        If the `Service` is created it defines how many `Node` instances shall be able to open it in
        parallel. If an existing `Service` is opened it defines how many `Node` instances must be at
        least supported.
        """
    def max_notifiers(self, /, value: int) -> ServiceBuilderEvent:
        """
        If the `Service` is created it defines how many `Notifier` shall be supported at most. If
        an existing `Service` is opened it defines how many `Notifier` must be at least supported.
        """
    def notifier_created_event(self, /, value: EventId) -> ServiceBuilderEvent:
        """
        If the `Service` is created it defines the event that shall be emitted by every newly
        created `Notifier`.
        """
    def notifier_dead_event(self, /, value: EventId) -> ServiceBuilderEvent:
        """
        If the `Service` is created it defines the event that shall be emitted when a
        `Notifier` is identified as dead.
        """
    def notifier_dropped_event(self, /, value: EventId) -> ServiceBuilderEvent:
        """
        If the `Service` is created it defines the event that shall be emitted by every
        `Notifier` before it is dropped.
        """
    def open(self, /) -> PortFactoryEvent:
        """
        Opens an existing `Service`. Emits an `EventOpenError` on failure.
        """
    def open_or_create(self, /) -> PortFactoryEvent:
        """
        If the `Service` exists, it will be opened otherwise a new `Service` will be
        created. On failure it emits an `EventOpenOrCreateError`
        """
    def open_or_create_with_attributes(self, /, verifier: AttributeVerifier) -> PortFactoryEvent:
        """
        If the `Service` exists, it will be opened otherwise a new `Service` will be
        created. It defines a set of attributes. If the `Service` already exists all attribute
        requirements must be satisfied otherwise the open process will fail. If the `Service`
        does not exist the required attributes will be defined in the `Service`.
        Emits and `EventOpenOrCreateError` on failure.
        """
    def open_with_attributes(self, /, verifier: AttributeVerifier) -> PortFactoryEvent:
        """
        Opens an existing `Service` with attribute requirements. If the defined attribute
        requirements are not satisfied the open process will fail. Emits an `EventOpenError`
        on failure.
        """

@final
class ServiceBuilderPublishSubscribe:
    """
    Builder to create a new `MessagingPattern.PublishSubscribe` based `Service`
    """
    def __flatbuffer_schema_path(self, /, path: FilePath) -> ServiceBuilderPublishSubscribe2: ...
    @property
    def __get_payload_type_details(self, /) -> Any | None: ...
    def __payload_type_details(self, /, value: TypeDetail) -> ServiceBuilderPublishSubscribe2:
        """
        Defines the payload type. To be able to connect to a `Service` the `TypeDetail` must be
        identical in all participants since the communication is always strongly typed.
        """
    def __set_payload_type(self, /, value: Any) -> None: ...
    def __set_user_header_type(self, /, value: Any) -> None: ...
    def __type_definition_name_hint(self, /, name: str, namespace: str) -> ServiceBuilderPublishSubscribe2: ...
    def __user_header_type_details(self, /, value: TypeDetail) -> ServiceBuilderPublishSubscribe2:
        """
        Defines the user header type. To be able to connect to a `Service` the `TypeDetail` must be
        identical in all participants since the communication is always strongly typed.
        """
    def create(self, /) -> PortFactoryPublishSubscribe:
        """
        Creates a new `Service`.
        On failure it emits `PublishSubscribeCreateError`.
        """
    def create_with_attributes(self, /, attributes: AttributeSpecifier) -> PortFactoryPublishSubscribe:
        """
        Creates a new `Service` with a set of attributes.
        On failure it emits `PublishSubscribeCreateError`.
        """
    def enable_safe_overflow(self, /, value: bool) -> ServiceBuilderPublishSubscribe2:
        """
        If the `Service` is created, defines the overflow behavior of the service. If an existing
        `Service` is opened it requires the service to have the defined overflow behavior.
        """
    def history_size(self, /, value: int) -> ServiceBuilderPublishSubscribe2:
        """
        If the `Service` is created it defines the maximum history size a `Subscriber` can request
        on connection. If an existing `Service` is opened it defines the minimum required.
        """
    def max_nodes(self, /, value: int) -> ServiceBuilderPublishSubscribe2:
        """
        If the `Service` is created it defines how many `Node` instances shall be able to open it in
        parallel. If an existing `Service` is opened it defines how many `Node` instances must be at
        least supported.
        """
    def max_publishers(self, /, value: int) -> ServiceBuilderPublishSubscribe2:
        """
        If the `Service` is created it defines how many `Publisher` shall be supported at
        most. If an existing `Service` is opened it defines how many `Publisher` must be at
        least supported.
        """
    def max_subscribers(self, /, value: int) -> ServiceBuilderPublishSubscribe2:
        """
        If the `Service` is created it defines how many `Subscriber` shall be supported at
        most. If an existing `Service` is opened it defines how many `Subscriber` must be at
        least supported.
        """
    def open(self, /) -> PortFactoryPublishSubscribe:
        """
        Opens an existing `Service`.
        On failure it emits `PublishSubscribeOpenError`.
        """
    def open_or_create(self, /) -> PortFactoryPublishSubscribe:
        """
        If the `Service` exists, it will be opened otherwise a new `Service` will be created.
        On failure it emits `PublishSubscribeOpenOrCreateError`
        """
    def open_or_create_with_attributes(self, /, verifier: AttributeVerifier) -> PortFactoryPublishSubscribe:
        """
        If the `Service` exists, it will be opened otherwise a new `Service` will be
        created. It defines a set of attributes. If the `Service` already exists all attribute
        requirements must be satisfied otherwise the open process will fail. If the `Service`
        does not exist the required attributes will be defined in the `Service`.
        On failure it emits `PublishSubscribeOpenOrCreateError`
        """
    def open_with_attributes(self, /, verifier: AttributeVerifier) -> PortFactoryPublishSubscribe:
        """
        Opens an existing `Service` with attribute requirements. If the defined attribute
        requirements are not satisfied the open process will fail.
        On failure it emits `PublishSubscribeOpenError`.
        """
    def payload_alignment(self, /, value: Alignment) -> ServiceBuilderPublishSubscribe2:
        """
        Overrides and increases the alignment of the payload - useful when the payload is used in
        SIMD operations. To be able to connect to a `Service` the payload alignment must be
        identical in all participants since the communication is always strongly typed.
        """
    def subscriber_max_borrowed_samples(self, /, value: int) -> ServiceBuilderPublishSubscribe2:
        """
        If the `Service` is created it defines the `Sample` count a
        `Subscriber` can borrow at most in parallel. If an existing
        `Service` is opened it defines the minimum required.
        """
    def subscriber_max_buffer_size(self, /, value: int) -> ServiceBuilderPublishSubscribe2:
        """
        If the `Service` is created it defines how many `Sample` a `Subscriber` can store in its
        internal buffer. If an existing `Service` is opened it defines the minimum required.
        """

@final
class ServiceBuilderRequestResponse:
    """
    Builder to create a new `MessagingPattern.RequestResponse` based `Service`
    """
    @property
    def __get_request_payload_type_details(self, /) -> Any | None: ...
    @property
    def __get_response_payload_type_details(self, /) -> Any | None: ...
    def __internal_request_flatbuffer_schema_path(self, /, path: FilePath) -> ServiceBuilderRequestResponse2:
        """
        Sets the path to the flatbuffer schema file for the Request. If this is not explicitly
        defined, iceoryx2 will try to find the best fitting schema file in the configured
        filebuffer schema paths defined in the config.
        """
    def __internal_request_type_definition_name_hint(self, /, name: str, namespace: str) -> ServiceBuilderRequestResponse2: ...
    def __internal_response_flatbuffer_schema_path(self, /, path: FilePath) -> ServiceBuilderRequestResponse2:
        """
        Sets the path to the flatbuffer schema file for the Response. If this is not explicitly
        defined, iceoryx2 will try to find the best fitting schema file in the configured
        filebuffer schema paths defined in the config.
        """
    def __internal_response_type_definition_name_hint(self, /, name: str, namespace: str) -> ServiceBuilderRequestResponse2: ...
    def __request_header_type_details(self, /, value: TypeDetail) -> ServiceBuilderRequestResponse2:
        """
        Defines the request header type. To be able to connect to a `Service` the `TypeDetail` must
        be identical in all participants since the communication is always strongly typed.
        """
    def __request_payload_type_details(self, /, value: TypeDetail) -> ServiceBuilderRequestResponse2:
        """
        Defines the payload type for requests. To be able to connect to a `Service` the
        `TypeDetail` must be identical in all participants since the communication is always
        strongly typed.
        """
    def __response_header_type_details(self, /, value: TypeDetail) -> ServiceBuilderRequestResponse2:
        """
        Defines the response header type. To be able to connect to a `Service` the `TypeDetail`
        must be identical in all participants since the communication is always strongly typed.
        """
    def __response_payload_type_details(self, /, value: TypeDetail) -> ServiceBuilderRequestResponse2:
        """
        Defines the payload type for responses. To be able to connect to a `Service` the
        `TypeDetail` must be identical in all participants since the communication is always
        strongly typed.
        """
    def __set_request_header_type(self, /, value: Any) -> None: ...
    def __set_request_payload_type(self, /, value: Any) -> None: ...
    def __set_response_header_type(self, /, value: Any) -> None: ...
    def __set_response_payload_type(self, /, value: Any) -> None: ...
    def create(self, /) -> PortFactoryRequestResponse:
        """
        Creates a new `Service`.
        On failure `RequestResponseCreateError` will be emitted.
        """
    def create_with_attributes(self, /, attributes: AttributeSpecifier) -> PortFactoryRequestResponse:
        """
        Creates a new `Service` with a set of attributes.
        On failure `RequestResponseCreateError` will be emitted.
        """
    def enable_fire_and_forget_requests(self, /, value: bool) -> ServiceBuilderRequestResponse2:
        """
        If the `Service` is created, defines the fire-and-forget behavior of the service for
        requests.
        """
    def enable_safe_overflow_for_requests(self, /, value: bool) -> ServiceBuilderRequestResponse2:
        """
        If the `Service` is created, defines the overflow behavior of the service for requests.
        If an existing `Service` is opened it requires the service to have the defined overflow
        behavior.
        """
    def enable_safe_overflow_for_responses(self, /, value: bool) -> ServiceBuilderRequestResponse2:
        """
        If the `Service` is created, defines the overflow behavior of the service for responses.
        If an existing `Service` is opened it requires the service to have the defined overflow
        behavior.
        """
    def max_active_requests_per_client(self, /, value: int) -> ServiceBuilderRequestResponse2:
        """
        Defines how many active requests a `Server` can hold in
        parallel per `Client`. The objects are used to send answers to a request that was
        received earlier from a `Client`.
        """
    def max_borrowed_responses_per_pending_response(self, /, value: int) -> ServiceBuilderRequestResponse2:
        """
        If the `Service` is created it defines the `Response` count that shall
        be able to be borrowed in parallel per `PendingResponse`. If an
        existing `Service` is opened it defines how many borrows must be at least supported.
        """
    def max_clients(self, /, value: int) -> ServiceBuilderRequestResponse2:
        """
        If the `Service` is created it defines how many `Client` ports shall
        be supported at most. If an existing `Service` is opened it defines how many
        `Client` ports must be at least supported.
        """
    def max_loaned_requests(self, /, value: int) -> ServiceBuilderRequestResponse2:
        """
        If the `Service` is created it defines how many `RequestMut` a
        `Client` can loan in parallel.
        """
    def max_nodes(self, /, value: int) -> ServiceBuilderRequestResponse2:
        """
        If the `Service` is created it defines how many `Node` instances shall
        be able to open it in parallel. If an existing `Service` is opened it defines how many
        `Node` instances must be at least supported.
        """
    def max_response_buffer_size(self, /, value: int) -> ServiceBuilderRequestResponse2:
        """
        If the `Service` is created it defines how many responses fit in the
        `Client`'s buffer. If an existing `Service` is opened it defines the minimum required.
        """
    def max_servers(self, /, value: int) -> ServiceBuilderRequestResponse2:
        """
        If the `Service` is created it defines how many `Server` ports shall
        be supported at most. If an existing `Service` is opened it defines how many
        `Server` ports must be at least supported.
        """
    def open(self, /) -> PortFactoryRequestResponse:
        """
        Opens an existing `Service`.
        On failure `RequestResponseOpenError` will be emitted.
        """
    def open_or_create(self, /) -> PortFactoryRequestResponse:
        """
        If the `Service` exists, it will be opened otherwise a new `Service` will be created.
        On failure `RequestResponseOpenOrCreateError` will be emitted.
        """
    def open_or_create_with_attributes(self, /, verifier: AttributeVerifier) -> PortFactoryRequestResponse:
        """
        If the `Service` exists, it will be opened otherwise a new `Service` will be
        created. It defines a set of attributes.

        If the `Service` already exists all attribute requirements must be satisfied,
        and service payload type must be the same, otherwise the open process will fail.
        If the `Service` does not exist the required attributes will be defined in the `Service`.
        On failure `RequestResponseOpenOrCreateError` will be emitted.
        """
    def open_with_attributes(self, /, verifier: AttributeVerifier) -> PortFactoryRequestResponse:
        """
        Opens an existing `Service` with attribute requirements. If the defined attribute
        requirements are not satisfied the open process will fail.
        On failure `RequestResponseOpenError` will be emitted.
        """
    def request_payload_alignment(self, /, value: Alignment) -> ServiceBuilderRequestResponse2:
        """
        Overrides and increases the alignment of the request payload - useful when the payload is
        used in SIMD operations. To be able to connect to a `Service` the payload alignment must be
        identical in all participants since the communication is always strongly typed.
        """
    def response_payload_alignment(self, /, value: Alignment) -> ServiceBuilderRequestResponse2:
        """
        Overrides and increases the alignment of the response payload - useful when the payload is
        used in SIMD operations. To be able to connect to a `Service` the payload alignment must be
        identical in all participants since the communication is always strongly typed.
        """

@final
class ServiceDetails:
    """
    Represents all the `Service` information that one can acquire with `Service.list`.
    """
    def __str__(self, /) -> str: ...
    def attributes(self, /) -> AttributeSet:
        """
        Returns the attributes of the `Service`
        """
    def messaging_pattern(self, /) -> MessagingPattern:
        """
        Returns the `Service`'s underlying `MessagingPattern`.
        """
    def name(self, /) -> ServiceName:
        """
        Returns the `ServiceName`
        """
    def nodes(self, /) -> list[NodeState]:
        """
        A list of every `Node` that is registered at the `Service`
        """
    def service_hash(self, /) -> ServiceHash:
        """
        Returns the unique `ServiceHash` of the `Service`
        """

@final
class ServiceHash:
    """
    The unique id of a `Service`
    """
    @property
    def as_str(self, /) -> str:
        """
        Returns a String containing the `ServiceHash` value
        """
    @staticmethod
    def max_number_of_characters() -> int:
        """
        Returns the maximum string length of a `ServiceHash`
        """

@final
class ServiceName:
    """
    Relocatable (inter-process shared memory compatible) ``SemanticString`` implementation for
    `ServiceName`. All modification operations ensure that never an
    invalid file or path name can be generated. All strings have a fixed size so that the maximum
    path or file name length the system supports can be stored.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @staticmethod
    def max_len() -> int:
        """
        Returns the maximum length of a `ServiceName`
        """
    @staticmethod
    def new(name: str) -> ServiceName:
        """
        Creates a new `ServiceName` when the provided ``name`` contains a valid path to a file,
        otherwise it emits a `SemanticStringError`.
        """
    def to_string(self, /) -> str:
        """
        Converts the `ServiceName` into a `str`
        """

@final
class ServiceType:
    """
    Defines the type of the `Service` and what kind of resources and operating system mechanisms
    it shall use.
    """
    Ipc: Final[ServiceType]
    """
    Optimized for inter-process communication.
    """
    Local: Final[ServiceType]
    """
    Optimized for inter-thread communication does not not support inter-process communication.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __int__(self, /) -> int: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __repr__(self, /) -> str: ...
    def __str__(self, /) -> str: ...

@final
class SignalHandlingMode:
    """
    Defines how signals are handled by constructs that might register a custom
    ``SignalHandler``
    """
    Disabled: Final[SignalHandlingMode]
    """
    No signal handler will be registered.
    """
    HandleTerminationRequests: Final[SignalHandlingMode]
    """
    The signals `Signal.Interrupt` and `Signal.Terminate` are registered and
    handled. If such a ``Signal`` is received the user will be notified.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __int__(self, /) -> int: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __repr__(self, /) -> str: ...
    def __str__(self, /) -> str: ...

@final
class StaticConfigBlackboard:
    """
    The static configuration of an `MessagingPattern.Blackboard` based `Service`. Contains
    all parameters that do not change during the lifetime of a `Service`.
    """
    @property
    def max_nodes(self, /) -> int:
        """
        Returns the maximum supported amount of `Node` instances that can open the `Service`
        in parallel.
        """
    @property
    def max_readers(self, /) -> int:
        """
        Returns the maximum supported amount of `Reader` ports
        """
    @property
    def type_details(self, /) -> TypeDetail:
        """
        Returns the type details of the `Service`.
        """

@final
class StaticConfigEvent:
    """
    The static configuration of an `MessagingPattern.Event`
    based service. Contains all parameters that do not change during the lifetime of a
    `Service`.
    """
    @property
    def deadline(self, /) -> Duration | None:
        """
        Returns the deadline of the service. If no new notification is signaled from any
        `Notifier` after the given deadline, it is rated as an error and every `Listener` that is
        attached to a `WaitSet` is woken up and notified about the missed
        """
    @property
    def event_id_max_value(self, /) -> int:
        """
        Returns the largest `EventId` that is supported by the service
        """
    @property
    def max_listeners(self, /) -> int:
        """
        Returns the maximum supported amount of `Listener` ports
        """
    @property
    def max_nodes(self, /) -> int:
        """
        Returns the maximum supported amount of `Node` instances that can open the `Service`
        in parallel.
        """
    @property
    def max_notifiers(self, /) -> int:
        """
        Returns the maximum supported amount of `Notifier` ports
        """
    @property
    def notifier_created_event(self, /) -> EventId | None:
        """
        Returns the emitted `EventId` when a new notifier is created.
        """
    @property
    def notifier_dead_event(self, /) -> EventId | None:
        """
        Returns the emitted `EventId` when a notifier is identified as dead.
        """
    @property
    def notifier_dropped_event(self, /) -> EventId | None:
        """
        Returns the emitted `EventId` when a notifier is dropped.
        """

@final
class StaticConfigPublishSubscribe:
    """
    The static configuration of an `MessagingPattern.PublishSubscribe` based `Service`. Contains
    all parameters that do not change during the lifetime of a `Service`.
    """
    @property
    def has_safe_overflow(self, /) -> bool:
        """
        Returns true if the `Service` safely overflows, otherwise false. Safe
        overflow means that the `Publisher` will recycle the oldest
        `Sample` from the `Subscriber` when its buffer
        is full.
        """
    @property
    def history_size(self, /) -> int:
        """
        Returns the maximum history size that can be requested on connect.
        """
    @property
    def max_nodes(self, /) -> int:
        """
        Returns the maximum supported amount of `Node` instances that can open the `Service`
        in parallel.
        """
    @property
    def max_publishers(self, /) -> int:
        """
        Returns the maximum supported amount of `Publisher` ports
        """
    @property
    def max_subscribers(self, /) -> int:
        """
        Returns the maximum supported amount of `Subscriber` ports
        """
    @property
    def message_type_details(self, /) -> MessageTypeDetails:
        """
        Returns the type details of the `Service`.
        """
    @property
    def subscriber_max_borrowed_samples(self, /) -> int:
        """
        Returns how many `Sample` a `Subscriber` port can borrow in parallel at most.
        """
    @property
    def subscriber_max_buffer_size(self, /) -> int:
        """
        Returns the maximum supported buffer size for `Subscriber` port
        """

@final
class StaticConfigRequestResponse:
    """
    The static configuration of an `MessagingPattern.RequestResponse` based service. Contains all
    parameters that do not change during the lifetime of a `Service`.
    """
    @property
    def does_support_fire_and_forget_requests(self, /) -> bool:
        """
        Returns true if a fire and forget `RequestMut` can be sent from the `Client`, otherwise
        false.
        """
    @property
    def has_safe_overflow_for_requests(self, /) -> bool:
        """
        Returns true if the request buffer of the `Service` safely overflows, otherwise false.
        Safe overflow means that the `Client` will recycle the oldest requests from the
        `Server` when its buffer is full.
        """
    @property
    def has_safe_overflow_for_responses(self, /) -> bool:
        """
        Returns true if the response buffer of the `Service` safely overflows, otherwise false.
        Safe overflow means that the `Server` will recycle the oldest responses from the
        `Client` when its buffer is full.
        """
    @property
    def max_active_requests_per_client(self, /) -> int:
        """
        Returns the maximum of active requests a `Server` can hold in parallel per `Client`.
        """
    @property
    def max_borrowed_responses_per_pending_response(self, /) -> int:
        """
        Returns the maximum borrowed `Response` count a `Client` can hold in parallel per
        `PendingResponse`
        """
    @property
    def max_clients(self, /) -> int:
        """
        Returns the maximum number of supported `Client` ports for the `Service`.
        """
    @property
    def max_loaned_requests(self, /) -> int:
        """
        Returns the maximum number of `RequestMut` a `Client` can loan in parallel.
        """
    @property
    def max_nodes(self, /) -> int:
        """
        Returns the maximum number of supported `Node` instances for the `Service`.
        """
    @property
    def max_response_buffer_size(self, /) -> int:
        """
        Returns the maximum buffer size for responses for a `PendingResponse`.
        """
    @property
    def max_servers(self, /) -> int:
        """
        Returns the maximum number of supported `Server` ports for the `Service`.
        """
    @property
    def request_message_type_details(self, /) -> MessageTypeDetails:
        """
        Returns the request type details of the `Service`.
        """
    @property
    def response_message_type_details(self, /) -> MessageTypeDetails:
        """
        Returns the response type details of the `Service`.
        """

@final
class Subscriber:
    """
    Represents the receiving endpoint of a publish-subscribe based communication.
    """
    @property
    def buffer_size(self, /) -> int:
        """
        Returns the internal buffer size of the `Subscriber`.
        """
    def delete(self, /) -> None:
        """
        Releases the `Subscriber`.

        After this call the `Subscriber` is no longer usable!
        """
    def has_samples(self, /) -> bool:
        """
        Returns true if the `Subscriber` has samples in the buffer that can be received with
        `Subscriber.receive`. Emits `ConnectionFailure` on error.
        """
    @property
    def id(self, /) -> UniqueSubscriberId:
        """
        Returns the `UniqueSubscriberId` of the `Subscriber`
        """
    @property
    def name(self, /) -> PortName:
        """
        Returns the `PortName` of the `Subscriber`
        """
    def receive(self, /) -> Sample2 | None:
        """
        Receives a `Sample` from `Publisher`. If no sample could be received `None` is returned.
        If a failure occurs `ReceiveError` is returned.
        """

@final
class TypeDetail:
    """
    Contains all type details required to connect to a `Service`
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    def alignment(self, /, alignment: int) -> TypeDetail:
        """
        Sets the alignment of the type
        """
    @staticmethod
    def new() -> TypeDetail:
        """
        Creates a new `TypeDetail` for the unit type. Meaning size == 0, alignment == 1
        """
    def size(self, /, size: int) -> TypeDetail:
        """
        Sets the size of the type
        """
    def type_name(self, /, name: TypeName) -> TypeDetail:
        """
        Sets the unique `TypeName` of the type
        """
    def type_variant(self, /, value: TypeVariant) -> TypeDetail:
        """
        Defines the `TypeVariant` of the defined type. `TypeVariant.FixedSize` if the type has
        always the same size like an `ctypes.c_uint64` or `TypeVariant.Dynamic` when it is a dynamic
        array or vector
        """

@final
class TypeName:
    """
    Represents the string name of a type. The name shall uniquely identify the type in the
    communication system.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @staticmethod
    def max_len() -> int:
        """
        The maximum supported length of a `TypeName`
        """
    @staticmethod
    def new(name: str) -> TypeName:
        """
        Creates a new `TypeName`. If the provided ``name`` exceeds the maximum supported length
        it emits an `SemanticStringError`.
        """
    def to_string(self, /) -> str:
        """
        Returns the underlying `str` of the `TypeName`
        """

@final
class TypeVariant:
    """
    Defines if the type is a slice with a runtime-size (`TypeVariant.Dynamic`)
    or if its a type that satisfies `Sized` (`TypeVariant.FixedSize`).
    """
    Dynamic: Final[TypeVariant]
    """
    A dynamic sized type like a slice (dynamic array)
    """
    FixedSize: Final[TypeVariant]
    """
    A fixed size type like `ctypes.c_uint64`
    """
    def __int__(self, /) -> int: ...
    def __repr__(self, /) -> str: ...

@final
class UniqueClientId:
    """
    The system-wide unique id of a `Client`.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @property
    def value(self, /) -> int:
        """
        Returns the underlying raw value of the ID
        """

@final
class UniqueListenerId:
    """
    The system-wide unique id of a `Listener`.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @property
    def value(self, /) -> int:
        """
        Returns the underlying raw value of the ID
        """

@final
class UniqueNodeId:
    """
    The system-wide unique id of a `Node`
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    def pid(self, /, service_type: ServiceType) -> int:
        """
        Returns the process id of the process that owns the `Node`.
        """
    @property
    def value(self, /) -> int:
        """
        Returns the underlying integer value of the `UniqueNodeId`.
        """

@final
class UniqueNotifierId:
    """
    The system-wide unique id of a `Notifier`.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @property
    def value(self, /) -> int:
        """
        Returns the underlying raw value of the ID
        """

@final
class UniquePublisherId:
    """
    The system-wide unique id of a `Publisher`.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @property
    def value(self, /) -> int:
        """
        Returns the underlying raw value of the ID
        """

@final
class UniqueReaderId:
    """
    The system-wide unique id of a `Reader`.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @property
    def value(self, /) -> int:
        """
        Returns the underlying raw value of the ID
        """

@final
class UniqueServerId:
    """
    The system-wide unique id of a `Server`.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @property
    def value(self, /) -> int:
        """
        Returns the underlying raw value of the ID
        """

@final
class UniqueServiceId:
    """
    The system-wide unique id of a `Service`.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @property
    def value(self, /) -> int:
        """
        Returns the underlying raw value of the ID
        """

@final
class UniqueSubscriberId:
    """
    The system-wide unique id of a `Subscriber`.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @property
    def value(self, /) -> int:
        """
        Returns the underlying raw value of the ID
        """

@final
class UniqueWriterId:
    """
    The system-wide unique id of a `Writer`.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __str__(self, /) -> str: ...
    @property
    def value(self, /) -> int:
        """
        Returns the underlying raw value of the ID
        """

@final
class WaitSet:
    """
    The `WaitSet` implements a reactor pattern and allows to wait on multiple events in one
    single call `WaitSet.wait_and_process` until a interrupt or termination signal was received.

    The `Listener` can be attached as well as sockets or anything else that is a `FileDescriptor`.

    Can be created via the `WaitSetBuilder`.
    """
    def attach_deadline(self, /, attachment: Listener, deadline: Duration) -> WaitSetGuard:
        """
        Attaches a `Listener` as deadline to the `WaitSet`. Whenever the event is received or the
        deadline is hit, the user is informed in `WaitSet.wait_and_process`.
        The object cannot be attached twice and the
        `WaitSet.capacity` is limited by the underlying implementation.
        Whenever the object emits an event the deadline is reset by the `WaitSet`.
        """
    def attach_deadline_fd(self, /, attachment: FileDescriptor, deadline: Duration) -> WaitSetGuard:
        """
        Attaches a `FileDescriptor` as deadline to the `WaitSet`. Whenever the event is received or
        the deadline is hit, the user is informed in `WaitSet.wait_and_process`.
        The object cannot be attached twice and the
        `WaitSet.capacity` is limited by the underlying implementation.
        Whenever the object emits an event the deadline is reset by the `WaitSet`.
        """
    def attach_interval(self, /, interval: Duration) -> WaitSetGuard:
        """
        Attaches a tick event to the `WaitSet`. Whenever the timeout is reached the `WaitSet`
        informs the user in `WaitSet.wait_and_process`.
        """
    def attach_notification(self, /, attachment: Listener) -> WaitSetGuard:
        """
        Attaches a `Listener` as notification to the `WaitSet`. Whenever an event is received on the
        object the `WaitSet` informs the user in `WaitSet.wait_and_process` to handle the event.
        The object cannot be attached twice and the
        `WaitSet.capacity` is limited by the underlying implementation.
        """
    def attach_notification_fd(self, /, attachment: FileDescriptor) -> WaitSetGuard:
        """
        Attaches a `FileDescriptor` as notification to the `WaitSet`. Whenever an event is received on the
        object the `WaitSet` informs the user in `WaitSet.wait_and_process` to handle the event.
        The object cannot be attached twice and the
        `WaitSet.capacity` is limited by the underlying implementation.
        """
    @property
    def capacity(self, /) -> int:
        """
        Returns the capacity of the `WaitSet`
        """
    def delete(self, /) -> None:
        """
        Releases the `WaitSet`.

        After this call the `WaitSet` is no longer usable!
        """
    @property
    def is_empty(self, /) -> bool:
        """
        Returns true if the `WaitSet` has no attachments, otherwise false.
        """
    @property
    def len(self, /) -> int:
        """
        Returns the number of attachments.
        """
    @property
    def signal_handling_mode(self, /) -> SignalHandlingMode:
        """
        Returns the `SignalHandlingMode` with which the `WaitSet` was created.
        """
    def wait_and_process(self, /) -> tuple[list[WaitSetAttachmentId], WaitSetRunResult]:
        """
        Waits until an event arrives on the `WaitSet`, then collects the events corresponding
        `WaitSetAttachmentId` in a vector and returns it.

        If an interrupt- (`signal.SIGINT`) or a termination-signal (`signal.SIGTERM`) was received,
        it will exit the loop and inform the user with `WaitSetRunResult.Interrupt` or
        `WaitSetRunResult.TerminationRequest`.

        **Important:** The `WaitSet` only reports that an attachment is ready; it
        does not consume the notification or data that caused the wake-up. If the
        callback returns without consuming any pending input, the attachment remains
        ready and the `WaitSet` wakes up again immediately. Repeating this can cause
        a busy loop and high CPU usage.

        For a `Listener`, consume pending notifications with `Listener.try_wait`.
        For a socket or another file-descriptor-based attachment, consume the pending
        data using its corresponding read or receive API.
        """
    def wait_and_process_with_timeout(self, /, timeout: Duration) -> tuple[list[WaitSetAttachmentId], WaitSetRunResult]:
        """
        Waits until an event arrives on the `WaitSet` or the provided timeout has passed, then
        collects the events corresponding `WaitSetAttachmentId` in a vector and returns it.

        If an interrupt- (`signal.SIGINT`) or a termination-signal (`signal.SIGTERM`) was received,
        it will exit the loop and inform the user with `WaitSetRunResult.Interrupt` or
        `WaitSetRunResult.TerminationRequest`.

        **Important:** The `WaitSet` only reports that an attachment is ready; it
        does not consume the notification or data that caused the wake-up. If the
        callback returns without consuming any pending input, the attachment remains
        ready and the `WaitSet` wakes up again immediately. Repeating this can cause
        a busy loop and high CPU usage.

        For a `Listener`, consume pending notifications with `Listener.try_wait`.
        For a socket or another file-descriptor-based attachment, consume the pending
        data using its corresponding read or receive API.
        """

@final
class WaitSetAttachmentId:
    """
    Represents an attachment to the `WaitSet`
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __hash__(self, /) -> int: ...
    def __ne__(self, /, other: object) -> bool: ...
    @staticmethod
    def from_guard(guard: WaitSetGuard) -> WaitSetAttachmentId:
        """
        Creates an `WaitSetAttachmentId` from a `WaitSetGuard` that was returned via
        `WaitSet.attach_interval`, `WaitSet.attach_notification` or
        `WaitSet.attach_deadline`.
        """
    def has_event_from(self, /, other: WaitSetGuard) -> bool:
        """
        Returns true if an event was emitted from a notification or deadline attachment
        corresponding to `WaitSetGuard`.
        """
    def has_missed_deadline(self, /, other: WaitSetGuard) -> bool:
        """
        Returns true if the deadline for the attachment corresponding to `WaitSetGuard` was missed.
        """

@final
class WaitSetBuilder:
    """
    Creates a new `WaitSet`.
    """
    def create(self, /) -> WaitSet:
        """
        Creates the `WaitSet`.
        """
    def signal_handling_mode(self, /, value: SignalHandlingMode) -> WaitSetBuilder:
        """
        Defines the `SignalHandlingMode` for the `WaitSet`. It affects the
        `WaitSet.wait_and_process` and `WaitSet.wait_and_process_with_timeout` calls
        that returns any received ``Signal`` via its `WaitSetRunResult` return value.
        """

@final
class WaitSetGuard:
    """
    Is returned when something is attached to the `WaitSet`. As soon as it goes out
    of scope, the attachment is detached.
    """
    def delete(self, /) -> None:
        """
        Drops the `WaitSetGuard`. After this call the `WaitSetGuard` is no longer usable.
        """

@final
class WaitSetRunResult:
    """
    States why the `WaitSet.wait_and_process` method returned.
    """
    AllEventsHandled: Final[WaitSetRunResult]
    """
    All events were handled.
    """
    Interrupt: Final[WaitSetRunResult]
    """
    An interrupt signal `signal.SIGINT` was received.
    """
    StopRequest: Final[WaitSetRunResult]
    """
    The users callback returned `CallbackProgression.Stop`.
    """
    TerminationRequest: Final[WaitSetRunResult]
    """
    A termination signal `signal.SIGTERM` was received.
    """
    def __eq__(self, /, other: object) -> bool: ...
    def __int__(self, /) -> int: ...
    def __ne__(self, /, other: object) -> bool: ...
    def __repr__(self, /) -> str: ...
    def __str__(self, /) -> str: ...

@final
class Writer:
    """
    Represents the writing endpoint of a blackboard based communication.
    """
    def __entry(self, /, key: int, value_type_details: TypeDetail) -> EntryHandleMut2:
        """
        Creates an `EntryHandleMut` for direct write access to the value. There can be only one
        `EntryHandleMut` per value. On failure it returns `EntryHandleMutError` describing the
        failure.
        """
    @property
    def __key_type_details(self, /) -> Any | None: ...
    def delete(self, /) -> None:
        """
        Releases the `Writer`.

        After this call the `Writer` is no longer usable!
        """
    @property
    def id(self, /) -> UniqueWriterId:
        """
        Returns the `UniqueWriterId` of the `Writer`
        """
    @property
    def name(self, /) -> PortName:
        """
        Returns the `PortName` of the `Writer`
        """

def set_log_level(value: LogLevel) -> None:
    """
    Sets the current log level. This is ignored for external frameworks like ``log`` or ``tracing``.
    Here you have to use the log-level settings of that framework.

    # Important

    When using external frameworks, the log level should be set explicitly, as
    only messages matching that level will be forwarded. You may also need to
    configure the framework’s own log level settings.
    """

def set_log_level_from_env_or(value: LogLevel) -> None:
    """
    Sets the log level by reading environment variable "IOX2_LOG_LEVEL", and if the environment variable
    doesn't exit it sets it with a user-defined logging level

    # Important

    When using external frameworks, the log level should be set explicitly, as
    only messages matching that level will be forwarded. You may also need to
    configure the framework’s own log level settings.
    """

def set_log_level_from_env_or_default() -> None:
    """
    Sets the log level by reading environment variable "IOX2_LOG_LEVEL" or default it with `LogLevel.Info`

    # Important

    When using external frameworks, the log level should be set explicitly, as
    only messages matching that level will be forwarded. You may also need to
    configure the framework’s own log level settings.
    """

def __getattr__(name: str) -> Incomplete: ...
