The objectlog package provides a customizable log for a single object.  The
system was designed to provide information for a visual log of important
object changes and to provide analyzable information for metrics.

- It provides automatic recording for each log entry of a timestamp and the
  principals in the request when the log was made.

- Given a schema of data to collect about the object, it automatically
  calculates and stores changesets from the last log entry, primarily to
  provide a quick and easy answer to the question "what changed?" and
  secondarily to reduce database size.

- It accepts optional summary and detail values that allow the system or users
  to annotate the entries with human-readable messages.

- It allows each log entry to be annotated with zero or more marker interfaces
  so that log entries may be classified with an interface.

For more information about using zc.objectlog, see:

    src/zc/objectlog/log.txt
