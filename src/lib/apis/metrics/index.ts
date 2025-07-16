import { WEBUI_API_BASE_URL } from '$lib/constants';

type Metrics = {
    id: number;
    user_id: string;
    chat_id: string;
    selected_model_id: string;
    date: Date; // string format: '2025-07-12' i.e. '%Y-%m-%d'

    input_tokens: number;
    output_tokens: number;
    message_count: number;
};

type ChatMetrics = {
    chat_id: string

    input_tokens: number;
    output_tokens: number;
    message_count: number;
}

export type { Metrics };

export const getMetrics = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/metrics/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getMetricsByChats = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/metrics/chats`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getMetricsByChatId = async (token: string, chat_id: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/metrics/${chat_id}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

