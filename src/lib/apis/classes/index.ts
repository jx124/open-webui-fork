import { WEBUI_API_BASE_URL } from '$lib/constants';

export type ClassForm = {
	id: number,
	name: string,
	instructor_id: string,
	image_url: "",
	assignments: Assignment[],
	assigned_students: string[],
}

export type Assignment = {
	class_id: number,
	prompt_id: number,
	deadline: string | null,

	allow_multiple_attempts: boolean,
	allow_submit_after_deadline: boolean
}

export const getClassList = async (token: string = '') => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/classes/`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const createNewClass = async (
    token: string = '', form_data: ClassForm
) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/classes/create`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		},
        body: JSON.stringify(form_data)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
            console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};


export const getClassById = async (
    token: string = '', classId: number
) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/classes/${classId}`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
            console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getAssignmentSubmissions = async (
    token: string = '', classId: number
) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/classes/${classId}/assignments/list`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
            console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const updateClass = async (
    token: string = '', form_data: ClassForm
) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/classes/update`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		},
        body: JSON.stringify(form_data)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
            console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const deleteClassById = async (token: string, classId: number) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/classes/delete/${classId}`, {
		method: 'DELETE',
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
			error = err.detail;
			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};


export const downloadChatsByClassId = async (token: string, classId: number) => {
	let error = null;
	let filename = "";

	const res = await fetch(`${WEBUI_API_BASE_URL}/classes/${classId}/download`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/zip',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			const disposition = res.headers.get('Content-Disposition');
			filename = disposition?.split(/;(.+)/)[1].split(/=(.+)/)[1] ?? "Unknown Class-export.zip";
			if (filename.toLowerCase().startsWith("utf-8''"))
				filename = decodeURIComponent(filename.replace("utf-8''", ''));
			else
				filename = filename.replace(/['"]/g, '');
			return res.blob();
		})
		.then((blob) => {
			const url = window.URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = filename;
			document.body.appendChild(a);
			a.click();
			window.URL.revokeObjectURL(url);
		})
		.catch((err) => {
			error = err.detail;
			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
}