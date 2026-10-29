# Lightning: Bitcoin's Express Lane

> The Lightning Network is a second layer built on top of bitcoin that makes small payments fast and cheap. Instead of recording every payment on bitcoin's main ledger, Lightning lets payments zip back and forth and only settles up on the main ledger now and then. River's app can send and receive over Lightning or the regular way. Lightning is for spending-sized amounts. Long-term savings still belong in the slow, safe lane.

You don't need Lightning to save in bitcoin. I don't use it for my weekly buys. But you'll hear the word a lot, and it's worth knowing what it is in plain English.

## The toll tag

Picture a toll road. The old way, every car stops at the booth, rolls down the window, and pays. It works. It's also slow, and when traffic's heavy, the line backs up.

Then toll tags came along. You set up an account once, stick a little tag on your windshield, and drive through the express lane without stopping. The tolls add up in the background and settle with your account later.

Bitcoin's main network is the booth. Lightning is the toll tag.

## The main road: on-chain

Every regular bitcoin payment gets written into the **blockchain**, which is bitcoin's public record book. Everyone running bitcoin keeps a copy. That's what makes it so hard to cheat. It's also why it's slow on purpose. New pages get added about every ten minutes, and there's only so much room on each page.

When the road is busy, people pay higher **network fees** to get their payment on the next page. Those fees go to **miners**, the folks who add the pages. A regular payment like this is called **on-chain**.

For moving a chunk of savings to your own wallet, on-chain is great. You do it once in a while, and you want the strongest settlement there is.

For buying a coffee? Waiting and paying a fee for a $5 purchase makes no sense.

## The express lane: Lightning

Lightning sits on top of bitcoin. Two parties open a **channel**, which is like a shared tab, by putting some bitcoin into it with one on-chain transaction. After that, they can send payments back and forth inside the channel as often as they want, almost instantly, without writing each one into the record book. When they're done, they close the channel and the final balance gets recorded on-chain.

Channels link together into a network. So you don't need a direct channel with the coffee shop. Your payment hops through other channels to get there.

To get paid on Lightning, you usually share an **invoice**, which is a long code or QR code that says how much and where. The sender scans it and pays.

## How it works on River

River's wallet lets you send and receive bitcoin either way, on-chain or over Lightning, as of October 2026. When you receive, you pick which kind of request to make. When you send, you scan or paste what the other person gave you.

My own savings setup stays on the main road. I buy weekly on River, and River auto-withdraws to my cold storage hardware wallet on-chain once my balance hits an amount I picked. I wrote about that in [Auto-Withdrawals](/p/bitcoin-auto-withdrawals/). Lightning is the tool you'd reach for when you want to send a small amount fast, like paying a friend back.

## The honest part

Lightning is built for spending money, not savings. It's the express lane, not the parking garage. Most Lightning wallets are online, which makes them handier and more exposed. Keep big amounts on-chain in storage you control.

Lightning is newer and more complicated under the hood than regular bitcoin. If something goes wrong, there's no bank to call.

And Lightning doesn't change the price. Bitcoin swings hard and can stay down for years. River is also a company with its own risks. Only put in money you can leave alone.

## Questions I get about this

### Is Lightning a different coin?

No. It's the same bitcoin, moving on a faster layer on top of the main network. That's different from the thousands of other coins out there, which I cover in [Bitcoin vs. Crypto](/p/bitcoin-vs-crypto/).

### Do I need Lightning to save in bitcoin?

No. If you're buying a little each week and holding, you may never use it. It's handy for sending small amounts quickly.

### Can I send Lightning to someone who doesn't use River?

Yes. Lightning works between different wallets, as long as theirs supports it. They give you an invoice, and you pay it.

## Sources

- [River: How do I send bitcoin?](https://support.river.com/hc/en-us/articles/45489800672915-How-do-I-send-bitcoin): sending on-chain or over Lightning in the River app.
- [River: How do I receive bitcoin?](https://support.river.com/hc/en-us/articles/50059696568723-How-do-I-receive-bitcoin): receiving either way.
- [River wallet](https://river.com/wallet): River's send and receive features.
- [River Learn: What is the Lightning Network?](https://river.com/learn/what-is-the-lightning-network/): further reading on channels and how payments hop.

---

Want to try sending a few sats over Lightning? [Open a River account with my link](https://river.com/signup?r=EYL3QNCO). It's an affiliate link: when you buy your first $100, we each get $5 in bitcoin, then $15 more each at $1,000 and $80 more each at $10,000, up to $100 apiece. River isn't available in every state.

*Bitcoin's price swings hard and can stay down for years, so only use money you can leave alone. I publish [exactly what I earn](/what-i-earn/). Nothing here is financial, tax, or legal advice. I'm a regular guy who did the homework, sharing what I learned. You make your own calls.*
