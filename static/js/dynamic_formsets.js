$(document).ready(function () {
    const maxImages = 5;

    function updateItemNumbers() {
        $('.item-form').each(function (index) {
            $(this).attr('data-index', index);
            $(this).find('.item-number').text(index + 1);

            // 이미지 컨테이너 ID 및 버튼 data-index도 갱신
            $(this).find('.image-container').attr('id', `image-container-${index}`);
            $(this).find('.add-image').attr('data-index', index);
            $(this).find('.image-management-form').attr('data-index', index);
        });
    }

    // 이미지 미리보기 및 HEIC 변환
    $(document).on('change', '.image-input', function () {
        const fileInput = this;
        const file = fileInput.files[0];
        const $form = $(fileInput).closest('.image-form');
        const $preview = $form.find('.image-preview');

        if (!file) return;

        $preview.hide();
        let $loader = $form.find('.image-loading');
        if ($loader.length === 0) {
            $loader = $(`
                <div class="image-loading text-center p-2">
                    <div class="spinner-border text-secondary" role="status" style="width: 1.5rem; height: 1.5rem;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div>변환 중...</div>
                </div>
            `);
            $form.find('.image-preview-wrapper').append($loader);
        }

        if (file.name.toLowerCase().endsWith('.heic')) {
            heic2any({
                blob: file,
                toType: "image/jpeg",
                quality: 0.9
            }).then(function (convertedBlob) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    $preview.attr('src', e.target.result).show();
                    $loader.remove();
                };
                reader.readAsDataURL(convertedBlob);

                const newFile = new File(
                    [convertedBlob],
                    file.name.replace(/\.heic$/i, ".jpg"),
                    { type: "image/jpeg", lastModified: new Date().getTime() }
                );
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(newFile);
                fileInput.files = dataTransfer.files;
            }).catch(function (err) {
                alert('HEIC 파일 변환 중 오류가 발생했습니다: ' + err.message);
                $loader.html('<div class="text-danger">변환 실패</div>');
            });
            return;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            $preview.attr('src', e.target.result).show();
            $loader.remove();
        };
        reader.readAsDataURL(file);
    });

    // 이미지 삭제
    $(document).on('click', '.delete-image', function () {
        const $itemForm = $(this).closest('.item-form');
        const index = $itemForm.data('index');
        const container = $(`#image-container-${index}`);
        const totalFormsInput = $(`input[name="images-${index}-TOTAL_FORMS"]`);
        const imageForms = container.find('.image-form');

        if (imageForms.length > 1) {
            $(this).closest('.image-form').remove();
            totalFormsInput.val(imageForms.length - 1);
        } else {
            alert('최소 한 개의 이미지는 등록해야 합니다.');
        }
    });

    // 이미지 추가
    $(document).on('click', '.add-image', function () {
        const index = $(this).data('index');
        const container = $(`#image-container-${index}`);
        const totalFormsInput = $(`input[name="images-${index}-TOTAL_FORMS"]`);
        let formCount = parseInt(totalFormsInput.val());

        if (formCount >= maxImages) {
            alert('이미지는 품목당 최대 5개까지만 추가할 수 있습니다.');
            return;
        }

        const firstForm = container.find('.image-form:first');
        const newForm = firstForm.clone();

        newForm.find('input, select, textarea').each(function () {
            const name = $(this).attr('name');
            const id = $(this).attr('id');
            if (name) {
                const newName = name.replace(/(images-\d+)-\d+/, `images-${index}-${formCount}`);
                $(this).attr('name', newName);
            }
            if (id) {
                const newId = id.replace(/(id_images-\d+)-\d+/, `id_images-${index}-${formCount}`);
                $(this).attr('id', newId);
            }
            $(this).val('');
        });


        newForm.find('.image-preview').hide().attr('src', '');
        newForm.find('.image-loading').remove();
        newForm.find('input[type="file"]').addClass('image-input');

        container.append(newForm);
        totalFormsInput.val(formCount + 1);
    });

    // 품목 삭제
    $(document).on('click', '.delete-item', function () {
        if ($('.item-form').length > 1) {
            $(this).closest('.item-form').remove();
            updateItemNumbers();
        } else {
            alert('최소 1개의 품목은 남겨야 합니다.');
        }
    });

    // 품목 추가
    const totalItemsInput = $('#id_items-TOTAL_FORMS');
    const itemContainer = $('#formset-container');
    const itemTemplate = itemContainer.children('.item-form:first').clone();

    $('#add-item-btn').on('click', function () {
        let formIdx = parseInt(totalItemsInput.val());
        const newItem = itemTemplate.clone();

        // 폼 필드 이름/ID 갱신
        newItem.find('input, select, textarea').each(function () {
            const name = $(this).attr('name');
            const id = $(this).attr('id');
            if (name) {
                const newName = name
                    .replace(/items-\d+-/, `items-${formIdx}-`)
                    .replace(/images-\d+-/, `images-${formIdx}-`);
                $(this).attr('name', newName);
            }
            if (id) {
                const newId = id
                    .replace(/id_items-\d+-/, `id_items-${formIdx}-`)
                    .replace(/id_images-\d+-/, `id_images-${formIdx}-`);
                $(this).attr('id', newId);
            }
            $(this).val('');
        });


        // 이미지 미리보기 초기화
        newItem.find('.image-preview').hide().attr('src', '');
        newItem.find('.image-loading').remove();
        newItem.find('.image-form').not(':first').remove();

        // 이미지 container ID 및 버튼 data-index 지정
        const imageContainer = newItem.find('.image-container');
        imageContainer.attr('id', `image-container-${formIdx}`);
        newItem.find('.add-image').attr('data-index', formIdx);

        // 관리 form 클론 및 갱신
        const mgmtFormSource = $('.image-management-form[data-index="0"]').clone();
        mgmtFormSource.attr('data-index', formIdx);
        mgmtFormSource.find('input[type="hidden"]').each(function () {
            const name = $(this).attr('name').replace(/images-0-/, `images-${formIdx}-`);
            const id = $(this).attr('id').replace(/id_images-0-/, `id_images-${formIdx}-`);
            $(this).attr({ name, id });

            if (name.endsWith('-INITIAL_FORMS')) {
                $(this).val('0');
            } else if (name.endsWith('-TOTAL_FORMS')) {
                $(this).val('1');
            }
        });

        imageContainer.before(mgmtFormSource);

        // 첫 번째 이미지 필드도 새 인덱스로 갱신
        newItem.find('.image-form:first input').each(function () {
            const name = $(this).attr('name');
            const id = $(this).attr('id');
            if (name && id) {
                const newName = name.replace(/images-\d+-\d+-/, `images-${formIdx}-0-`);
                const newId = id.replace(/id_images-\d+-\d+-/, `id_images-${formIdx}-0-`);
                $(this).attr({ name: newName, id: newId }).val('');
            }
        });

        itemContainer.append(newItem);
        totalItemsInput.val(formIdx + 1);
        updateItemNumbers();
    });
});
