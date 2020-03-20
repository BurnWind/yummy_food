$(function(){
	$('#add_product').click(function(){
		$('.add_product').show()
		$('.products_msg').hide()
	})
	$('#product_msg').click(function(){
		$('.products_msg').show()
		$('.add_product').hide()
	})


	$('#add_sbum').click(function(e){       
		var yan = true
        e.preventDefault()
        if(!$('.arow input[name=product_name]').val()){
            alert('商品描述不能为空')
            yan = false
        }else if(!$(".arow input[name=product_total]").val()){
            alert('商品库存不能为空')
            yan = false
        }else if(!$(".arow input[name=product_price]").val()){
            alert('商品价格不能为空')
            yan = false
        }else if($(".arow input[name=banner]").val().length<2){
            alert('请至少选择两张商品banner图')
            yan = false
        }else if(!$(".arow input[name=detail]").val()){
            alert('请至少选择一张商品详情图')
            yan = false
        }else{
            yan = true
        }
        if(yan){
            var formdata = new FormData($('#aform')[0])
            $.ajax({
                url:'/add_product',
                type:'post',
                dataType:'text',
                data:formdata,
                processData: false,
                contentType: false,
                success:function(data){
                    alert(data)
                    location.href='/index'
                },
                error:function(data){
                    alert(data.responseText)
                }
            })
        }

	})

	// 表格语言设置
	var lang = {
	    "sProcessing": "处理中...",
	    "sLengthMenu": "每页 _MENU_ 项",
	    "sZeroRecords": "没有匹配结果",
	    "sInfo": "当前显示第 _START_ 至 _END_ 项，共 _TOTAL_ 项。",
	    "sInfoEmpty": "当前显示第 0 至 0 项，共 0 项",
	    "sInfoFiltered": "(由 _MAX_ 项结果过滤)",
	    "sInfoPostFix": "",
	    // "sSearch": "本地搜索：",
	    "sUrl": "",
	    "sEmptyTable": "暂无数据",
	    "sLoadingRecords": "载入中...",
	    "sInfoThousands": ",",
	    "oPaginate": {
	        "sFirst": "首页",
	        "sPrevious": "上页",
	        "sNext": "下页",
	        "sLast": "末页",
	        "sJump": "跳转"
	    },
	    "oAria": {
	        "sSortAscending": ": 以升序排列此列",
	        "sSortDescending": ": 以降序排列此列"
	    }
	};
	// 表格
	var table = $('#products').DataTable({
	           "processing" : true, //DataTables载入数据时，是否显示进度条
	           "serverSide": false,  //  开启服务端模式
	            "language": lang, //提示信息 
	            // "sScrollX" : 1000, //DataTables的宽
	             "lengthMenu": [10, 20, 30],   // 显示每页显示的条数  
	            "stripeClasses": ["odd", "even"],   // 为奇偶行添加样式
	            "searching": true,       // 是否允许开启本地检索功能
	            "bFilter": false,         // 去掉 搜索框
	            "paging": true,            // 是否开启本地分页
	            "lengthChange": true, //是否允许产品改变表格每页显示的记录数
	            "info": true,             // 控制是否显示表格左下角的信息
	            "bSort": false, // 禁止排序
	            "deferRender": true,   // 延迟渲染
	             "pageLength": 10,      // 每页显示的条数
	                                    //跟数组下标一样，第一列从0开始，这里表格初始化时，
	            "order": [2, 'asc'],   //asc升序   desc降序 // 下标为2，第三列 生序排列
	            "aoColumnDefs": [{
	                "orderable": false,// 指定列不参与排序
	                "aTargets": [] // 指定 下标为[1,3,4,5,6]的不排序 
	            }],
	            "ajax": {  // ajax 请求数据
	                "url": "/get_products",
	                "type": "get",
                    "dataType": "json",
	            },
	            "columns":[
		            { data: 'product_name' },
                    { data: 'product_kind_id' },
				    { data: 'product_kind' },
				    { data: 'product_price' },
				    { data: 'product_total' },
				    { data: 'product_sellnum'}
				]
	    
	    
	});

	// 获取行数据
	$('#products tbody').on('click', 'tr', function () {
        var data = table.row(this).data();
    } );
})