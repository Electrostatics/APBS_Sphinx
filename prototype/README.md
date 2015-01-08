# Sphinx Prototype
## Introduction
The purpose of this prototype is to illustrate some ideas I have for the
project, and yet thus far, have been unable to convey.

## Points Worth Mention
### Plug-in Modules
Plug-in modules provide all the useful functionality of Sphinx.

### Semantic Databus
Data is shared betwixt the plug-ins via what I've dubbed the **Semantic
Databus**, or **SDB**.  The core idea here is that we don't want to become
obsolete as soon as we define an API.  We need a way to share data between
modules that we don't even know about.

This is where the *semantic* bit comes in play.  We define an extensible data
ontology that we use to tag data.

The first level of abstraction is the **record**, which contains a complete
datum.  The SDB surfaces a function to retrieve a record from a *named* data
source.

A record consists of a hash whose keys are semantic tags, and values are the
data itself.  For hierarchal data, a value may itself be another hash.  If a
value is not hierarchal, and still has a cardinality greater than one, it will
be presented as an array.  The implication is that the ordering of the values
is unimportant.  If the order matters, then the data should be tagged.

Each plug-in is responsible for maintaining its own data store.  When the SDB
is queried for a record, it passes that query to the plug-in, which should then
provide the record asynchronously.  This implies that a plug-in may reads data
asynchronously, e.g., from a file, or over a network.

*...thinking out loud...*
Let's not tag sources and sinks, but the data itself.

For file types we have a file-type tag, that plug-ins can use to specify the
type of file they read.  Sphinx itself can surface values of file-type based
on extension, *magic number*, or something else.  This would let us wrap the
file itself as data with a tag that's the type of file.  Thus making it
consistent with the tagged data model.

The data read from a file will be partitioned and tagged by the input plug-in,
according to whatever is appropriate for the data in the file, as determined by
the plug-in.

Consumers of the data will query by **record**, which is the standard
subdivision for data.  Each record will contain tagged fields.  *How are the
fields accessed?  Is it an array?  A mapping of tag to value?  What if there
are multiple values per tag?*

I'm leaning towards a hash of tags.  A tag with multiple values would contain a
sub-hash of tagged values.
*...end of musings...*


### Sinks and Sources
Data flows from a *Source* to a *Sink*.  A particular plug-in may be a source,
a sink, or both.

## Plug-in Modules
As previously mentioned, plug-ins may be sources, or sinks, and typically both.
For some reason, I've chosen to hyphenate plug-in in favor of the single word
variant: plugin.

### Read a File
A plug-in that *groks* a particular file format registers itself with the SDB
as such by specifying the format in terms of a set of file extensions.  When a
file with one of these extensions is to be ingested by Sphinx, this plug-in is
called upon to read the file.  The data that is read may then be queried by
subsequent plug-ins.

The format for registration is *SDB_source({file-type: [ext, ...]})*.

### Write a File
The format for registration is *SDB_sink({file-type: [ext, ...]})*.

### Process a Command File
Command files specify a flow of data between plug-ins.  They are declarative
in nature, which simplifies creation of data pipelines.

### C Example
Example of a plug-in that is linked to some C code.

## Included Examples
There are a few different examples included.

### Read / Transform / Write
This example pipeline reads the contents of a file and converts lowercase
letters to uppercase.

The salient points are that there is a

### Streaming

### Tee Pipeline

## Potentially Useful Plug-ins
* Chemical Markup Language (CML) Importer
