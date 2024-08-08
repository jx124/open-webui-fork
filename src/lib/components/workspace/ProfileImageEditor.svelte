<script lang="ts">
	import { canvasPixelTest, generateInitialsImage } from "$lib/utils";
	import { getContext } from "svelte";

	let profileImageInputElement: HTMLInputElement;
	const i18n = getContext('i18n');

    export let image_url: string;
    export let default_image = "/user.png";
    export let initialsSource: string;
</script>

<input
    id="profile-image-input"
    bind:this={profileImageInputElement}
    type="file"
    hidden
    accept="image/*"
    on:change={(e) => {
        const files = profileImageInputElement.files ?? [];
        let reader = new FileReader();
        reader.onload = (event) => {
            let originalImageUrl = `${event.target.result}`;

            const img = new Image();
            img.src = originalImageUrl;

            img.onload = function () {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');

                // Calculate the aspect ratio of the image
                const aspectRatio = img.width / img.height;

                // Calculate the new width and height to fit within 100x100
                let newWidth, newHeight;
                if (aspectRatio > 1) {
                    newWidth = 100 * aspectRatio;
                    newHeight = 100;
                } else {
                    newWidth = 100;
                    newHeight = 100 / aspectRatio;
                }

                // Set the canvas size
                canvas.width = 100;
                canvas.height = 100;

                // Calculate the position to center the image
                const offsetX = (100 - newWidth) / 2;
                const offsetY = (100 - newHeight) / 2;

                // Draw the image on the canvas
                ctx?.drawImage(img, offsetX, offsetY, newWidth, newHeight);

                // Get the base64 representation of the compressed image
                const compressedSrc = canvas.toDataURL('image/jpeg');

                // Display the compressed image
                image_url = compressedSrc;

                profileImageInputElement.files = null;
            };
        };

        if (
            files.length > 0 &&
            ['image/gif', 'image/webp', 'image/jpeg', 'image/png'].includes(files[0]['type'])
        ) {
            reader.readAsDataURL(files[0]);
        }
    }}
/>

<div class="flex space-x-5">
    <div class="flex flex-col">
        <div class="self-center mt-2">
            <button
                class="relative rounded-full dark:bg-gray-700"
                type="button"
                on:click={() => {
                    profileImageInputElement.click();
                }}
            >
                <img
                    src={image_url !== '' ? image_url : default_image}
                    alt="profile"
                    class="rounded-full h-24 w-24 object-cover"
                />

                <div
                    class="absolute flex justify-center rounded-full bottom-0 left-0 right-0 top-0 h-full w-full overflow-hidden bg-gray-700 bg-fixed opacity-0 transition duration-300 ease-in-out hover:opacity-50"
                >
                    <div class="my-auto text-gray-100">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                            class="w-5 h-5"
                        >
                            <path
                                d="m2.695 14.762-1.262 3.155a.5.5 0 0 0 .65.65l3.155-1.262a4 4 0 0 0 1.343-.886L17.5 5.501a2.121 2.121 0 0 0-3-3L3.58 13.419a4 4 0 0 0-.885 1.343Z"
                            />
                        </svg>
                    </div>
                </div>
            </button>
        </div>
    </div>

    <div class="flex-1 flex flex-col self-center gap-0.5">
        <div class=" mb-0.5 text-sm font-medium">{$i18n.t('Profile Image')}</div>

        <div>
            <button
                class=" text-xs text-center text-gray-800 dark:text-gray-400 rounded-full px-4 py-0.5 bg-gray-100 dark:bg-gray-850"
                type="button"
                on:click={async () => {
                    if (canvasPixelTest()) {
                        image_url = generateInitialsImage(initialsSource);
                    } else {
                        toast.info(
                            $i18n.t(
                                'Fingerprint spoofing detected: Unable to use initials as avatar. Defaulting to default profile image.'
                            ),
                            {
                                duration: 1000 * 10
                            }
                        );
                    }
                }}>{$i18n.t('Use Initials')}</button
            >

            <button
                class=" text-xs text-center text-gray-800 dark:text-gray-400 rounded-lg px-2 py-1"
                type="button"
                on:click={async () => {
                    image_url = default_image;
                }}>{$i18n.t('Remove')}</button
            >
        </div>
    </div>
</div>