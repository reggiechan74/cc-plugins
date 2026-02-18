import { google } from "googleapis";

export async function lookupContact(auth, email) {
  const people = google.people({ version: "v1", auth });

  try {
    const searchResponse = await people.people.searchContacts({
      query: email,
      readMask: "names,emailAddresses,organizations,photos",
      pageSize: 5,
    });

    const results = (searchResponse.data.results || [])
      .map((result) => {
        const person = result.person;
        if (!person) return null;

        const names = person.names || [];
        const emails = person.emailAddresses || [];
        const orgs = person.organizations || [];
        const photos = person.photos || [];

        const matchingEmail = emails.find(
          (e) => e.value?.toLowerCase() === email.toLowerCase()
        );
        if (!matchingEmail) return null;

        return {
          displayName: names[0]?.displayName || "",
          givenName: names[0]?.givenName || "",
          familyName: names[0]?.familyName || "",
          email: matchingEmail.value,
          organization: orgs[0]?.name || "",
          title: orgs[0]?.title || "",
          photoUrl: photos[0]?.url || "",
        };
      })
      .filter(Boolean);

    if (results.length === 0) {
      return { found: false, email, message: `No contact found for ${email}` };
    }

    return { found: true, email, contacts: results };
  } catch (error) {
    if (error.code === 403 || error.code === 401) {
      return {
        found: false,
        email,
        message: `Contact lookup unavailable: ${error.message}. Ensure contacts.readonly scope is authorized.`,
      };
    }
    throw new Error(`Failed to lookup contact: ${error.message}`);
  }
}
