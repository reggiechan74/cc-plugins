export async function createFilter(gmail, criteria, action) {
  try {
    const response = await gmail.users.settings.filters.create({
      userId: "me",
      requestBody: { criteria, action },
    });
    return response.data;
  } catch (error) {
    if (error.code === 400) {
      throw new Error(`Invalid filter criteria or action: ${error.message}`);
    }
    throw new Error(`Failed to create filter: ${error.message}`);
  }
}

export async function listFilters(gmail) {
  try {
    const response = await gmail.users.settings.filters.list({ userId: "me" });
    const filters = response.data.filters || [];
    return { filters, count: filters.length };
  } catch (error) {
    throw new Error(`Failed to list filters: ${error.message}`);
  }
}

export async function getFilter(gmail, filterId) {
  try {
    const response = await gmail.users.settings.filters.get({
      userId: "me",
      id: filterId,
    });
    return response.data;
  } catch (error) {
    if (error.code === 404) {
      throw new Error(`Filter with ID "${filterId}" not found.`);
    }
    throw new Error(`Failed to get filter: ${error.message}`);
  }
}

export async function deleteFilter(gmail, filterId) {
  try {
    await gmail.users.settings.filters.delete({ userId: "me", id: filterId });
    return { success: true, message: `Filter "${filterId}" deleted successfully.` };
  } catch (error) {
    if (error.code === 404) {
      throw new Error(`Filter with ID "${filterId}" not found.`);
    }
    throw new Error(`Failed to delete filter: ${error.message}`);
  }
}

export const filterTemplates = {
  fromSender: (senderEmail, labelIds = [], archive = false) => ({
    criteria: { from: senderEmail },
    action: {
      addLabelIds: labelIds,
      removeLabelIds: archive ? ["INBOX"] : undefined,
    },
  }),
  withSubject: (subjectText, labelIds = [], markAsRead = false) => ({
    criteria: { subject: subjectText },
    action: {
      addLabelIds: labelIds,
      removeLabelIds: markAsRead ? ["UNREAD"] : undefined,
    },
  }),
  withAttachments: (labelIds = []) => ({
    criteria: { hasAttachment: true },
    action: { addLabelIds: labelIds },
  }),
  largeEmails: (sizeInBytes, labelIds = []) => ({
    criteria: { size: sizeInBytes, sizeComparison: "larger" },
    action: { addLabelIds: labelIds },
  }),
  containingText: (searchText, labelIds = [], markImportant = false) => ({
    criteria: { query: `"${searchText}"` },
    action: {
      addLabelIds: markImportant ? [...labelIds, "IMPORTANT"] : labelIds,
    },
  }),
  mailingList: (listIdentifier, labelIds = [], archive = true) => ({
    criteria: { query: `list:${listIdentifier} OR subject:[${listIdentifier}]` },
    action: {
      addLabelIds: labelIds,
      removeLabelIds: archive ? ["INBOX"] : undefined,
    },
  }),
};
