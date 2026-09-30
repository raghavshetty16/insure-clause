# ClauseCheck, explained in plain language

This is a walkthrough of what we built and why. No jargon that isn't explained. If you only
read one section, read "The one-sentence version" and "The five clerks".

---

## The problem

A health insurance policy is a 60-page rulebook. When someone makes a claim, whether the
company pays — and how much — depends on maybe five sentences buried somewhere in those 60
pages. Waiting periods, banned treatments, room-rent caps, per-procedure limits, the patient's
own share.

Today a human reads the rulebook and works it out by hand. It is slow, and the customer
usually gets a rejection letter that says "not payable" without saying *which rule* said so.

## The one-sentence version

**ClauseCheck is a clerk that reads the policy for you, shows you the exact sentences it relied
on, and does the arithmetic on a calculator instead of in its head.**

The "shows you the exact sentences" part is the whole point. Anyone can open the PDF and check
whether we quoted it correctly.

---

## Why this needs AI at all

You might ask: why not just write ordinary code with a big list of rules?

Because every insurer words things differently. One says "total or partial replacement of a
knee joint", another says "knee arthroplasty", a third says "joint replacement surgery". A
claim might say "knee replacement". Ordinary keyword code misses that. A language model
understands they mean the same thing.

But you also can't just *ask* a language model, because the answer isn't general knowledge —
it's specific to one insurer's document. Ask ChatGPT "what's the waiting period for knee
surgery" and it will confidently make up a number. **It has to read the actual document.**

That combination — needs understanding, must read a specific document — is exactly what RAG
(Retrieval Augmented Generation) is for. Retrieve the right pages, then answer only from them.

---

## Part 1: Cutting up the rulebook

Before we can find the right sentences, we have to chop the PDF into searchable pieces.

**The obvious way (which is wrong):** cut every 1,000 characters. Imagine cutting a cookbook
into equal-sized strips with scissors, ignoring where recipes start and end. You get the end of
the lasagne recipe glued to the start of the trifle. Now when someone asks about lasagne, you
hand them half a dessert.

**What we did:** cut along the document's own headings. A policy already has numbered sections —
`4.2 Specific Waiting Periods`, `5.1 Excluded Treatments`. We cut there, so each piece is one
complete rule. We also staple the heading onto the top of every piece, so the rule never gets
separated from its own title.

We also tag each piece: which insurer, which section number, which page, and what kind of rule
it is (waiting period / exclusion / room rent / etc.).

> **A bug we hit here.** Our tagger read the *body text* of each section. Section 5.1 is the
> list of banned treatments, and its text happens to say the bans are "not subject to any
> **waiting period**". So the tagger labelled the banned-treatments section as a waiting-period
> section. The fix: read the **heading** first, and only fall back to the body. Headings don't
> lie about what they are.

## Part 2: Finding the right pieces

We ask **two different librarians** and combine their answers.

- **Librarian A understands meaning.** Ask for "knee replacement" and she'll find "total or
  partial replacement of a knee joint". (Technically: vector embeddings.)
- **Librarian B is literal-minded** but never misses an exact match. Ask for "Clause 4.2" or
  "48 months" and he finds precisely that. (Technically: BM25 keyword search.)

Meaning-search alone misses exact clause numbers. Keyword-search alone misses synonyms. So we
ask both and merge their shortlists, favouring anything both liked.

**The rulebook filter.** Before either librarian starts, we lock them to *one* policy. This
matters more than it sounds. If we let them browse all three insurers' books, the system can
confidently quote Insurer A's waiting period while judging Insurer B's claim — and the answer
looks completely convincing. It's like answering a Monopoly rules question from the Scrabble
box. Right-sounding, totally wrong.

**The picky editor (re-ranking).** The two librarians hand back about 10 candidates. A third
model re-reads them and picks the best 4.

> **Something we measured and changed.** The class lab uses a particular editor model. We
> tested it on six questions where we knew the right answer, and it *made things worse* — it
> threw away the correct room-rent clause and the correct co-payment clause. It turned out that
> model is trained for a different job (deciding if a sentence answers a question), not for
> ranking. We swapped in a model built for ranking and got all six right. Same component, same
> code structure as the lab; different model inside.
>
> Honest footnote: with only ~18 pieces per policy, the two librarians already find the right
> clause every time. So re-ranking isn't what makes our system good here — its job is to *not
> break* what already works. We say that plainly rather than claiming credit for it.

---

## Part 3: The five clerks (the "agent")

This is the part that makes it an *agent* rather than a single question to a chatbot.

Instead of asking one big question, we run a small assembly line of five steps:

**1. The intake clerk** reads the claim and writes down the facts on a form: age, ailment, dates,
sum insured, bill amount, room rent. Then she writes a *checklist* of what needs looking up for
this particular claim. A knee replacement needs the waiting period, the per-procedure cap, and
the room rent rule. A dental claim mostly needs the banned-treatments list.

**2. The researcher** takes each checklist item and goes to the librarians for it.

**3. The reviewer** looks at what came back and asks: *does this actually answer the question?*
If yes, he writes the number down. If no, he **rewrites the search and sends it back** — this is
the loop, and it's the bit that makes this a genuine agent rather than a straight line. If the
second attempt also fails, he marks that item "couldn't establish".

**4. The calculator** does the arithmetic. Not the AI — actual Python code.

**5. The letter-writer** explains the decision to the customer in plain English, citing the
clauses.

### Why the calculator is separate (this is the important design decision)

Language models are genuinely bad at multi-step arithmetic. They'll confidently tell you
`8,000 × 0.625 = 5,200`.

So we split the job the way a shop works: **the assistant reads the prices off the shelf labels,
and the till adds them up.** You don't let the assistant do mental arithmetic and you don't ask
the till to find the products.

Here, the AI's only job is: find the clause, read the number out of it. Python then applies those
numbers in a fixed order:

1. Is this treatment banned outright? → pay nothing, stop.
2. Has the waiting period passed? → if not, pay nothing, stop.
3. Did they take a room above their limit? → reduce the whole bill proportionally.
4. Is there a cap on this procedure? → apply it.
5. Is the bill above the total cover? → cap it.
6. Is there a patient share (co-pay)? → deduct it.

Because this is ordinary code, the same claim always gives the same answer, and we can print
every step. **The AI cannot change the verdict — it only explains a verdict already decided.**

### Knowing when to shut up

If the reviewer couldn't establish something, the whole claim comes back as **"refer to human"**
rather than a guess. A clerk who says "I can't find this rule, please check" is more useful than
one who invents a plausible number. This is also the ethical position we'd defend: the system
assists an adjudicator, it doesn't reject people automatically.

### Handing back a proper form

We ask the AI to fill in a structured form (fixed fields, right data types). Sometimes it
scribbles outside the boxes. So we hand it back and ask again — twice. If it still can't, we
**raise an error** rather than guess what it meant. A crash you can see beats a wrong payout you
can't.

---

## Part 4: Proving it works

Claiming "our system is good" is worthless. So we built a **control group**.

We wrote 20 claim scenarios by hand, and for each one we worked out the right answer ourselves,
plus which clause decides it. Then we run two systems over the same 20:

- **The simple version**: chop the PDF into equal strips, one search, one question to the AI,
  "what's the answer?"
- **Ours**: everything described above.

Same claims, same documents, same model. The only difference is the machinery. That's a fair
A/B test, and it's the single most convincing thing we can show.

We measure five things: did it get the verdict right, the rupee amount right, cite the correct
clause, did the search even surface the right clause, and how much of its explanation is actually
supported by the documents.

> **A bug worth knowing about.** Nine of our 20 cases have a correct answer of ₹0 (claim
> rejected). A system that gives up on everything also outputs ₹0. So "refusing to answer" was
> scoring as *correct* on nearly half the test — a system that did nothing would have looked
> 45% accurate. We fixed it so giving up never counts as a correct amount, and we now report
> the give-up rate separately.

---

## Part 5: Where the project actually stands

**Working and checked:** the whole pipeline runs end to end. We verified 38 of the notebook's
cells execute cleanly. A real test case (a 64-year-old's knee replacement with three separate
deductions stacking) comes out at exactly the right figure, ₹1,20,000, citing the right clauses.

**Not done:** the comparison table has no numbers in it yet.

The reason is boring but hard: the free AI service allows 200,000 words'-worth of processing per
day. Our full test run needs about 264,000. It's a prepaid data pack and the test is bigger than
the pack. So the notebook now defaults to running 8 of the 20 cases, which fits.

We tried the smaller free model instead (it has its own daily allowance). It was noticeably
worse — on the knee replacement case it only did *one* of the four required lookups and came back
with ₹2,50,000 instead of ₹1,20,000. Like a trainee who skips most of the checklist. So we're not
using its results; reporting them would make our own system look worse than it is.

**To finish:** open the notebook on a fresh day and run it top to bottom.

---

## Part 6: Bugs we caught before the demo

Worth knowing because they're the kind of thing that gets asked about.

| What was wrong | The everyday version |
|---|---|
| Any clerk could fill in any box on the form, and we'd read it | The person answering "is this banned?" also scribbled a number in the "spending cap" box, and we used it as the cap. Now each clerk can only fill the box they were asked about. |
| If nobody checked the banned list, we assumed "not banned" | Silence was treated as permission. Now we *always* check the banned list, even if the intake clerk forgot to put it on the checklist. |
| We recorded age *now*, but some rules are about age *when you joined* | Like a gym discount based on your joining age, when all we wrote down was your age today. Added a second box to the form. |
| In the app, loading an example claim didn't switch the rulebook | You'd pick a claim from Insurer B while the system still had Insurer A's book open. The exact mistake our rulebook filter exists to prevent. |
| Results file was saved in a slightly broken format | It looked fine to us but other tools refused to open it. |

---

## How to run it

```bash
ollama pull nomic-embed-text      # the local meaning-search model
pip install -r requirements.txt
copy .env.example .env             # then paste your Groq key in
jupyter lab ClauseCheck.ipynb
```

Run the cells top to bottom. The app appears inside the notebook itself.

## One thing to be upfront about

The three policy documents in `data/policies/` are **not real insurance policies**. We wrote
them to look like real ones so we could build and test the system, and they say so on page 1.
They deliberately differ from each other (different waiting periods, different caps) so that the
"right rulebook" filter is visibly doing something.

Swapping in real downloaded policy PDFs is a five-minute job: drop them in the folder, update
the list file, re-run the indexing section.
