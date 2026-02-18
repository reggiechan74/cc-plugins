import { extractEmailContent } from "./email-utils.js";

export async function listThreads(gmail, query, maxResults = 10) {
  try {
    const response = await gmail.users.threads.list({
      userId: "me",
      q: query,
      maxResults,
    });

    const threads = response.data.threads || [];

    const results = await Promise.all(
      threads.map(async (thread) => {
        const detail = await gmail.users.threads.get({
          userId: "me",
          id: thread.id,
          format: "metadata",
          metadataHeaders: ["Subject", "From", "Date"],
        });

        const messages = detail.data.messages || [];
        const firstMessage = messages[0];
        const lastMessage = messages[messages.length - 1];
        const headers = firstMessage?.payload?.headers || [];

        return {
          id: thread.id,
          subject: headers.find((h) => h.name === "Subject")?.value || "",
          from: headers.find((h) => h.name === "From")?.value || "",
          date: headers.find((h) => h.name === "Date")?.value || "",
          messageCount: messages.length,
          lastMessageDate:
            lastMessage?.payload?.headers?.find((h) => h.name === "Date")?.value || "",
          snippet: detail.data.messages?.[0]?.snippet || "",
        };
      })
    );

    return results;
  } catch (error) {
    throw new Error(`Failed to list threads: ${error.message}`);
  }
}

export async function getThread(gmail, threadId, format = "full") {
  try {
    const response = await gmail.users.threads.get({
      userId: "me",
      id: threadId,
      format,
    });

    const messages = (response.data.messages || []).map((msg) => {
      const headers = msg.payload?.headers || [];
      const { text, html } = extractEmailContent(msg.payload || {});

      return {
        id: msg.id,
        threadId: msg.threadId,
        from: headers.find((h) => h.name?.toLowerCase() === "from")?.value || "",
        to: headers.find((h) => h.name?.toLowerCase() === "to")?.value || "",
        date: headers.find((h) => h.name?.toLowerCase() === "date")?.value || "",
        subject: headers.find((h) => h.name?.toLowerCase() === "subject")?.value || "",
        body: text || html || "",
        isHtml: !text && !!html,
        snippet: msg.snippet || "",
        labelIds: msg.labelIds || [],
      };
    });

    return {
      id: response.data.id,
      messageCount: messages.length,
      messages,
    };
  } catch (error) {
    if (error.code === 404) {
      throw new Error(`Thread "${threadId}" not found.`);
    }
    throw new Error(`Failed to get thread: ${error.message}`);
  }
}
