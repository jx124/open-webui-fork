import { WEBUI_API_BASE_URL } from '$lib/constants';

type RoleForm = {
	id: number;
	name: string;
};

export type { RoleForm };

export const getRoles = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/roles/`, {
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

export const updateUserRoles = async (token: string, userRoles: RoleForm[]) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/roles/update`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(
			userRoles
        )
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


export const deleteRoleById = async (token: string, roleId: number) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/roles/delete/${roleId}`, {
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
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};



// export const updateUserById = async (token: string, userId: string, user: UserUpdateForm) => {
// 	let error = null;

// 	const res = await fetch(`${WEBUI_API_BASE_URL}/users/${userId}/update`, {
// 		method: 'POST',
// 		headers: {
// 			'Content-Type': 'application/json',
// 			Authorization: `Bearer ${token}`
// 		},
// 		body: JSON.stringify({
// 			profile_image_url: user.profile_image_url,
// 			email: user.email,
// 			name: user.name,
// 			password: user.password !== '' ? user.password : undefined
// 		})
// 	})
// 		.then(async (res) => {
// 			if (!res.ok) throw await res.json();
// 			return res.json();
// 		})
// 		.catch((err) => {
// 			console.log(err);
// 			error = err.detail;
// 			return null;
// 		});

// 	if (error) {
// 		throw error;
// 	}

// 	return res;
// };
