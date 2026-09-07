# Accessibility

I want this site to work for everybody, including people who use a screen reader, navigate with a keyboard, zoom the page way in, or need bigger text and more spacing. That's not a legal box to tick. It's the same idea as the writing: plain, usable, no barriers.

## What I'm aiming for

Normaltown USA targets [WCAG 2.1 Level AA](https://www.w3.org/TR/WCAG21/), the standard most accessibility rules point to, including the Americans with Disabilities Act guidance from the Department of Justice.

## What's in place

- Every page has a "Skip to content" link so keyboard users can jump past the menu.
- Headings run in order, so screen reader users can navigate by structure instead of reading everything.
- Every image has a text description, and decorative images are hidden from screen readers.
- Links inside articles are underlined, so color is never the only thing marking a link.
- Text and background colors meet or beat the 4.5 to 1 contrast the standard asks for.
- The whole site works with a keyboard alone, and the focus outline is always visible.
- Pages reflow down to a 320 pixel wide screen and survive heavy zoom without losing content.
- Links that open a new tab say so for screen reader users.
- Contact form fields have real labels, and required fields are called out.
- If you've asked your device to reduce motion, the site honors that.

## The known gap

The email signup box in the footer is an embedded form from beehiiv, a third-party service, so I don't control its markup. Its text and background contrast is set correctly, and I add a name to the frame so screen readers announce it properly. What I can't add is a permanent visible label on the email field itself: beehiiv doesn't offer labels on a one-field form, so that field carries placeholder text instead, which disappears once you start typing. The instruction next to the form stays put and is read out with it.

If that form gives you trouble for any reason, [send me a message](/contact/) with your email address and I'll add you myself.

## Tell me if something's broken

If any part of this site doesn't work for you, I want to know, and I'll fix it. Use the [contact form](/contact/) and say what page you were on and what went wrong. I read every message myself and I'll write back.

This statement was last reviewed in September 2026.
