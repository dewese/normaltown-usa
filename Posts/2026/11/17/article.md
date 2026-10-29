# Auto-Withdrawals: How My Bitcoin Moves Itself to My Own Wallet

> An auto-withdrawal is a River setting that sends your bitcoin to a wallet you control once your balance reaches an amount you pick. I buy a little every week, it piles up on River, and when it hits my number it moves itself to my own hardware wallet. I don't have to remember to do it, and I don't leave a big pile sitting with a company.

Here's the whole thing in one sentence. River fills the jar, and when the jar hits the line, River carries it home for me.

That's it. The rest of this post is the why, the how, and the parts you need to be careful with.

## The coin jar on the counter

Picture a coin jar on your kitchen counter. Every day you drop your change in. You don't haul it to the bank every time you add a quarter. That would be silly. But you also don't want the jar to get so full that it's a real temptation for somebody walking by.

So you draw a line on the jar with a marker. When the coins reach the line, you take them to the bank and start over.

An auto-withdrawal is that marker line. My weekly buy is the change going in. River is the counter. My own wallet is the bank.

## What's actually happening

A few terms first, in plain English.

**Your own wallet** means a wallet where you hold the secret key, not a company. I explained keys in [Not Your Keys, Not Your Coins](/p/not-your-keys-what-it-means/), and wallets in [What a Bitcoin Wallet Actually Is](/p/what-is-a-bitcoin-wallet/).

**A hardware wallet** is a small device, about the size of a car key fob, that keeps your secret key offline. **Cold storage** just means the key lives somewhere that isn't connected to the internet. That's what I use.

**A threshold** is the amount you pick. As of October 2026, River lets you set it at 0.005 bitcoin or more. When your settled balance (bitcoin that's finished processing) reaches that amount, River sends it to the address you gave it. You can also choose to leave some bitcoin on River and only send the rest.

My setup looks like this:

1. An automatic recurring buy every week on River.
2. The bitcoin piles up in my River account.
3. Once it reaches the amount I picked, River sends it to my cold storage hardware wallet.
4. Repeat, forever, without me lifting a finger.

## Why I like it

The best savings plan is the one you don't have to remember. I wrote about that idea in [A Little Each Week Beats Betting It All](/p/a-little-each-week-beats-betting-it-all/). Auto-withdrawals do the same thing for storage that recurring buys do for buying.

It also means River never holds a big pile of mine for long. I trust River enough to buy there every week, and it publishes [proof that it holds client bitcoin](/p/proof-of-reserves-explained/). But a promise from any company is still a promise. Moving it home on a schedule keeps that trust small.

And the cost is easy to live with. As of October 2026, River gives you one free on-chain send each month. Beyond that, you pay a network fee, which goes to the miners who process the transaction, not to River. Picking a bigger threshold means fewer sends.

## The honest part

Self-custody means you're the bank now. If you lose your hardware wallet and your backup, nobody can get it back for you. No help desk. Before you turn this on, learn how backups work. I cover the master backup in [Your Seed Phrase Is the Master Key](/p/what-is-a-seed-phrase/).

The address has to be right. Bitcoin sent to the wrong address is gone. Get the address from your own wallet, double-check it, and send a small test first if you're new.

None of this changes the price. Bitcoin can drop hard and stay down for years. Moving it to your own wallet makes it safer from a company's problems, not from the market. Only buy what you can leave alone.

And River is a company with its own risks. This feature depends on River's app working the way it says. That's one more reason I like the coins not sitting there for long.

## Questions I get about this

### Do I need a hardware wallet to use auto-withdrawals?

No. It sends to any bitcoin address you control, including a phone wallet. River Learn's self-custody guide suggests starting small on a phone wallet and moving up to a hardware wallet as the amount grows. That's a sensible order.

### Can I change the amount or turn it off later?

Yes. You can edit or remove an auto-withdrawal in the River app. One wrinkle: if you turn on River's ForceField security limit, you can't create or edit auto-withdrawals while it's on, but existing ones keep running (as of October 2026). I explain ForceField in [the scams post](/p/bitcoin-scams-and-forcefield/).

### What does it cost?

As of October 2026, one on-chain send per month is free, and others pay a network fee. Set your threshold high enough that you're not sending tiny amounts all the time.

## Sources

- [River: What are bitcoin auto-withdrawals?](https://support.river.com/hc/en-us/articles/50085216806163-What-are-bitcoin-auto-withdrawals): how the threshold works and the 0.005 BTC minimum.
- [River: How do I start a bitcoin auto-withdrawal?](https://support.river.com/hc/en-us/articles/50081849656723-How-do-I-start-a-bitcoin-auto-withdrawal): the setup steps in the app.
- [River Learn: How to get started with bitcoin self custody](https://river.com/learn/how-to-get-started-self-custody/): further reading on holding your own keys, step by step.

---

Want to try this yourself? [Open a River account with my link](https://river.com/signup?r=EYL3QNCO). It's an affiliate link: when you buy your first $100, we each get $5 in bitcoin, then $15 more each at $1,000 and $80 more each at $10,000, up to $100 apiece. River isn't available in every state.

*Bitcoin's price swings hard and can stay down for years, so only use money you can leave alone. I publish [exactly what I earn](/what-i-earn/). Nothing here is financial, tax, or legal advice. I'm a regular guy who did the homework, sharing what I learned. You make your own calls.*
