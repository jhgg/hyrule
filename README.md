# hyrule
a proof of concept rules evaluation engine

## Project Status

This project is just me messing around with various ways a rules evaluation engine might work in Python.

## Concepts

In order to understand how Hyrule works, you need to understand a few concepts:
 - **Entity** An entity represents an object within Hyrule that has some significance in an external system. An enitity is defined by its `type` and `id`. A basic entity is a `User` (that is the type) and the user's id. 
 - **Label** An entity can have many labels attached to it. These labels are attached either by an operator, or by a the automated rules within Hyrule.
 - **Rule** A rule evaluates some preconditions and takes actions.
 - **Action** An action represents an intent to mutate labels attached to an Entity, along with the reason as to why the mutation is happening.

With the combination of entities, labels, rules and actions, we can build upon this a novel event classification system that can be used to enforce constraints, and detect bad actors within a system.

## An example

Let's suppose that we're managing an internet forum, and perhaps we want to deter spam based upon some rules. Let's say that we want to require the user to solve a captcha if they post over 5 posts an hour. 

At a high level, hyrule performs rules processing based on a rule-set + an event payload. In our fictitious example, our event payload might look like:

```json
{
    "action": "forum_post_created",
    "data": {
        "user": {
            "id": "12345",
            "email": "foo@jh.gg",
            "username": "jhgg"
        },
        "http": {
            "remote_addr": "17.32.51.2",
            "headers": {
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "close",
                "Dnt": "1",
                "Host": "myforum.org",
                "Referer": "https://google.com/",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
            }
        },
        "post": {
            "id": "551234",
            "topic": "Woah! Check out these deals!",
            "body": "Some link to some spam site"
        }
    }
}
```

We have a few entities here actually that we should disect:

   - **User/**`12345` - This User entity is commonly known as the `SessionActor` - or the person who is performing the action.
   - **Email/**`foo@jh.gg` - This `Email` goes alongside with the user, and is the e-mail of the user who is performing the action.
   - **Domain/**`jh.gg` - This domain, known as `EmailDomain` is the domain of the e-mail of the user who is performing the action. 
   - **Ip/**`17.32.51.2` - This `Ip` is the Ip address of the user who... (you get the idea).
   - **Post/**`551234` - And finally, this is the `CreatedContent`, which is the content on the system which was created. 


So, given the event data, we need to extract these entities out from the event payload. We might do this by defining the following feature extractors:

```py
# Here we are defining feature extractors for the user and e-mail.
SessionActor = Entity('User', JsonData('$.user.id'))
UserEmail = Entity('Email', JsonData('$.user.email'))
# Since domain is derived from e-mail, we are using the `ExtractDomain` function to pull
# the domain from the e-mail, and form it into an Entity.
UserEmailDomain = Entity('Domain', ExtractDomain(UserEmail))

# Likewise, we pull the Ip out, and we also pull out IpCountry by doing
# a geoip lookup on the Ip.
Ip = Entity('Ip', JsonData('$.http.remote_addr'))
IpCountry = Entity('Country', GeoIp(Ip, 'Country'))

# Finally, we create a feature for the created content, which is the post + id.
CreatedContent = Entity('Post', JsonData('$.post.id'))

# And we may use these in the future, perhaps for some basic string filtering.
PostTopic = JsonData('$.post.topic')
PostBody = JsonData('$.post.body')
```

Now, we can go ahead and create a basic rate limit rule:

```py
# This rate limit will evaluate to true, after we've processed 10 `forum_post_created` 
# events in a given hour. Alone, this rate limit doesn't do much, but we can then create
# a rule for this rate limit.
UserPostManyPostsLastHourRateLimit = RateLimit(
    by=User,
    max=10,
    per=Interval.Hours(1)
)

# This rule takes the rate limit, and says, when it evaluates to True,
# I will also evaluate to true.
UserPostManyPostsLastHourRule = Rule(
    when=[UserPostManyPostsLastHourRateLimit],
    reason="User posted 10 forum posts in an hour."
)

# A rule alone is not much though, and we need to now apply some labels.
WhenRules(
    rules=[UserPostManyPostsLastHourRule],
    then=[
        # Add a require captcha label to the session actor. An external
        # system might understand that this mean that now the user will
        # require a captcha solve to post again.
        Labels.Add(SessionActor, 'require_captcha'),
        # Also, let's go ahead and throw the post into a review queue, 
        # maybe a moderator might want to take a look and see if these
        # posts are legit. We'll let the post through, but we're going 
        # to flag it for mod review.
        Labels.Add(CreatedContent, 'require_moderator_review')
    ]
)
```

This at a high-level is how hyrule might work. This implementation begins to implement primitives that might make that possible, however, this is very much an experimental proof-of-concept. 


## What might be next? 

### Python as the rules language is a bad idea.

For the ease of prototyping, I've implemented the rules language in Python - or rather - by only using a very small amount of the Python syntax. Enough that I can go ahead and define the rules. However, a future and more correct  implementation might create a domain specific language to represent these rules. The concepts here expose the creation of a directed acyclic node graph from a python script, however, a language could be used to represent this, and the nodes could be created from a parsed AST - without any need for evaluation of Python code to create the graph. 

### Concurrent Execution of Unrelated Nodes on the Graph.

Not all resolvers and functions are constant time, some may depend on network or database calls. However, the dependency graph can be used to evaluate the rules, performing node resolution concurrently as it traverses the graph to evalulate the rule-set. 

### A backing store for entities, labels, rate limits, etc...

Hyrule leaves these up to the reader, and might provide interfaces that should be implemented in order to actually persist data. Seperating these things across an interface boundary makes a lot of sense here, as the purpose of hyrule is to describe a way in which rules would evaluate, but not a persistence model, as that can vary wildly depending on the scale at which these rules may be evaluated at.

### A backing store for events, and the outputs of rule evaluation.

Hyrule's purpose is to simply evalulate rules. It doesn't care about how the events are sourced, stored, or what the caller does with the result of the rule evaluations.

### Plugin System

In order to perform feature extraction meaningfully, a library of functions (e.g. geoip, e-mail normalization, user agent parsing, machine learning classifiers...), would need to be built. A plugin interface to expose functions which can be used in the rules would be neat. 